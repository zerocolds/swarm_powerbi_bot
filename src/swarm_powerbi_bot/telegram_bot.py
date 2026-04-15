from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .config import Settings
from .models import UserQuestion
from .orchestrator import SwarmOrchestrator
from .services.registration import get_user_object_id, is_subscribed, parse_start_arg, subscribe
# TODO: раскомментировать когда Ollama поддержит аудио-тракт
# from .services.stt_client import STTClient
from .services.sql_client import has_period_hint

# ── Inline-кнопки выбора периода ─────────────────────────────

PERIOD_BUTTONS = [
    [
        InlineKeyboardButton("Вчера", callback_data="period:вчера"),
        InlineKeyboardButton("Неделя", callback_data="period:за неделю"),
        InlineKeyboardButton("Месяц", callback_data="period:за месяц"),
    ],
    [
        InlineKeyboardButton("Квартал", callback_data="period:за квартал"),
        InlineKeyboardButton("Полгода", callback_data="period:за полгода"),
        InlineKeyboardButton("Год", callback_data="period:за год"),
    ],
]

PERIOD_KEYBOARD = InlineKeyboardMarkup(PERIOD_BUTTONS)


class TelegramSwarmBot:
    def __init__(self, token: str, orchestrator: SwarmOrchestrator, settings: Settings):
        self.token = token
        self.orchestrator = orchestrator
        self.settings = settings
        # TODO: раскомментировать когда Ollama поддержит аудио-тракт
        # self.stt = STTClient(settings)

    # ── /start [activation_link] ──────────────────────────────

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.effective_user:
            return

        account_id = str(update.effective_user.id)
        first_arg = context.args[0] if context.args else ""

        # Активация по ссылке: /start <customer_id>-<dataset_id>
        if first_arg and first_arg.strip():
            try:
                customer_id, dataset_id = parse_start_arg(first_arg)
                code, msg = await subscribe(customer_id, dataset_id, account_id, self.settings)
                await update.message.reply_text(msg)
            except ValueError as ve:
                await update.message.reply_text(f"⚠️ {ve}")
            except Exception:
                await update.message.reply_text("Техническая ошибка. Попробуйте позже.")
            return

        # Без аргумента — проверяем подписку и приветствуем
        try:
            already = await is_subscribed(account_id, self.settings)
        except Exception:
            already = False

        # TODO: раскомментировать когда Ollama поддержит аудио-тракт
        # voice_hint = ""
        # if self.stt.available:
        #     voice_hint = "\n\nМожно отправить голосовое сообщение — я пойму!"
        voice_hint = ""

        if already:
            await update.message.reply_text(
                "Вы подписаны! Просто напишите вопрос, например:\n"
                "• Покажи отток клиентов\n"
                "• Какая выручка за неделю?\n"
                "• Топ мастеров по загрузке"
                + voice_hint
            )
        else:
            await update.message.reply_text(
                "Привет! Я аналитический бот КДО.\n\n"
                "Просто напишите вопрос, например:\n"
                "• Покажи отток клиентов\n"
                "• Какая выручка за неделю?\n"
                "• Топ мастеров по загрузке\n\n"
                "Я определю тему и спрошу за какой период, "
                "если вы не указали его в вопросе."
                + voice_hint
            )

    # ── /ask <вопрос> ─────────────────────────────────────────

    async def ask(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return
        text = " ".join(context.args).strip()
        if not text:
            await update.message.reply_text("Пример: /ask Покажи тренд выручки за неделю")
            return
        await self._handle_user_text(update, context, text)

    # ── Обычное текстовое сообщение ───────────────────────────

    async def text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.message.text:
            return
        await self._handle_user_text(update, context, update.message.text.strip())

    # ── Голосовое сообщение (отключено — Ollama не поддерживает аудио-тракт) ──
    #
    # async def voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #     if not update.message or not update.message.voice:
    #         return
    #     if not self.stt.available:
    #         await update.message.reply_text(
    #             "Голосовые сообщения пока не поддерживаются — напишите текстом."
    #         )
    #         return
    #     await update.message.chat.send_action(action=ChatAction.TYPING)
    #     voice = update.message.voice
    #     file = await voice.get_file()
    #     audio_bytes = await file.download_as_bytearray()
    #     text = await self.stt.transcribe(bytes(audio_bytes), filename="voice.ogg")
    #     if not text:
    #         await update.message.reply_text(
    #             "Не удалось распознать. Попробуйте ещё раз или напишите текстом."
    #         )
    #         return
    #     await update.message.reply_text(f"🎤 _{text}_", parse_mode="Markdown")
    #     await self._handle_user_text(update, context, text)

    # ── Callback от inline-кнопки периода ─────────────────────

    async def period_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query or not query.data:
            return

        await query.answer()

        # Достаём сохранённый вопрос
        pending = (context.user_data or {}).get("pending_question", "")
        if not pending:
            await query.edit_message_text("Сессия истекла, задайте вопрос заново.")
            return

        # Извлекаем период из callback_data ("period:за неделю" → "за неделю")
        period_text = query.data.split(":", 1)[1]

        # Дополняем вопрос периодом
        full_question = f"{pending} {period_text}"

        # Убираем кнопки, показываем что выбрал пользователь
        await query.edit_message_text(f"📊 {pending} — *{period_text}*", parse_mode="Markdown")

        # Выполняем запрос — используем query.message для отправки ответа,
        # но user_id берём из callback_query.from_user (пользователь, не бот)
        if query.from_user:
            context.user_data["_callback_user_id"] = str(query.from_user.id)
        await self._process_question(query.message, full_question, context=context)

        # Очищаем pending
        context.user_data.pop("pending_question", None)

    # ── Внутренняя логика ─────────────────────────────────────

    async def _handle_user_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str,
    ) -> None:
        """Проверяет наличие периода. Если нет — показывает визард."""
        if not update.message:
            return

        if has_period_hint(text):
            # Период указан — выполняем сразу
            await self._process_question(update.message, text, context=context)
        else:
            # Период не указан — спрашиваем через кнопки
            context.user_data["pending_question"] = text
            await update.message.reply_text(
                f"📋 *{text}*\n\nЗа какой период?",
                reply_markup=PERIOD_KEYBOARD,
                parse_mode="Markdown",
            )

    async def _process_question(self, message, text: str, context: ContextTypes.DEFAULT_TYPE | None = None) -> None:
        await message.chat.send_action(action=ChatAction.TYPING)

        user_id = "unknown"
        # Для callback-запросов (period_callback) user_id сохранён из callback_query.from_user,
        # т.к. query.message.from_user — это бот, а не пользователь.
        user_data_raw = context.user_data if context else {}
        callback_uid = (user_data_raw or {}).pop("_callback_user_id", None)
        if callback_uid:
            user_id = callback_uid
        elif hasattr(message, "from_user") and message.from_user:
            user_id = str(message.from_user.id)
        elif hasattr(message, "chat") and message.chat:
            user_id = str(message.chat.id)

        # Получаем ObjectId (SalonId) из подписки — кэшируем в user_data
        object_id: int | None = None
        user_data = context.user_data if context else {}
        if user_data is not None:
            object_id = user_data.get("object_id")
            if object_id is None and user_id != "unknown":
                try:
                    object_id = await get_user_object_id(user_id, self.settings)
                    if object_id:
                        user_data["object_id"] = object_id
                except Exception:
                    pass
        # Fallback на default_object_id из конфига
        if object_id is None and self.settings.default_object_id:
            object_id = self.settings.default_object_id

        # last_topic для контекста разговора (follow-up вопросы)
        last_topic = ""
        if user_data is not None:
            last_topic = user_data.get("last_topic", "")

        response = await self.orchestrator.handle_question(
            UserQuestion(user_id=user_id, text=text, object_id=object_id,
                         last_topic=last_topic),
        )

        # Сохраняем тему для следующего вопроса
        if user_data is not None and response.topic:
            user_data["last_topic"] = response.topic

        if response.image:
            # Описание — caption к картинке (до 1024 символов)
            caption = self._fit_caption(response.answer)
            try:
                await message.reply_photo(
                    response.image, caption=caption, parse_mode="Markdown",
                )
            except Exception:
                # Markdown может сломаться — шлём без разметки
                await message.reply_photo(response.image, caption=caption)

            # Если ответ длиннее caption — шлём полный текст отдельно
            if len(response.answer) > 1024:
                try:
                    await message.reply_text(response.answer, parse_mode="Markdown")
                except Exception:
                    await message.reply_text(response.answer)
        else:
            try:
                await message.reply_text(response.answer, parse_mode="Markdown")
            except Exception:
                await message.reply_text(response.answer)

        # Follow-ups отдельным сообщением
        if response.follow_ups:
            hints = "\n".join(f"• {f}" for f in response.follow_ups[:3])
            try:
                await message.reply_text(
                    f"💡 *Что ещё можно спросить:*\n{hints}", parse_mode="Markdown",
                )
            except Exception:
                await message.reply_text(f"Что ещё можно спросить:\n{hints}")

    def run(self) -> None:
        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("ask", self.ask))
        app.add_handler(CallbackQueryHandler(self.period_callback, pattern=r"^period:"))
        # TODO: раскомментировать когда Ollama поддержит аудио-тракт
        # app.add_handler(MessageHandler(filters.VOICE, self.voice_message))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_message))
        app.run_polling(allowed_updates=Update.ALL_TYPES)

    @staticmethod
    def _fit_caption(text: str, limit: int = 1024) -> str:
        if len(text) <= limit:
            return text
        return text[: limit - 1].rstrip() + "…"
