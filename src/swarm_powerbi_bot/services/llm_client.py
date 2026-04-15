from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

import httpx

from ..config import Settings

logger = logging.getLogger(__name__)

# ── Промпт для LLM-планировщика запросов ──────────────────────

_PLANNER_SYSTEM_PROMPT = """\
Ты — планировщик SQL-запросов для дашборда салона красоты (КДО).
Пользователь задаёт вопрос на русском. Ты собираешь запрос из компонентов.

3 ПРОЦЕДУРЫ (выбери одну):

1. spKDO_Aggregate — агрегация визитов/выручки из tbRecords
   group_by: total | week | month | master | service | salon | channel
   Примеры:
   - «статистика за неделю» → group_by=total
   - «тренд по неделям» → group_by=week
   - «выручка по месяцам» → group_by=month
   - «мастера за месяц» → group_by=master
   - «топ услуг» → group_by=service
   - «сравни салоны» → group_by=salon
   - «каналы привлечения» → group_by=channel

2. spKDO_ClientList — список/агрегация клиентов по статусу из fnKDO_ClientStatus
   filter: all | outflow | leaving | forecast | noshow | quality | birthday
   group_by: list | status | master
   Примеры:
   - «отток за месяц» → filter=outflow, group_by=list
   - «уходящие клиенты» → filter=leaving, group_by=list
   - «прогноз визитов» → filter=forecast, group_by=list
   - «недошедшие» → filter=noshow, group_by=list
   - «контроль качества» → filter=quality, group_by=list
   - «все клиенты» → filter=all, group_by=list
   - «именинники» → filter=birthday, group_by=list
   - «отток по мастерам» → filter=outflow, group_by=master
   - «сколько в каждом статусе» → filter=all, group_by=status
   - «сравни отток по неделям» → НЕТ, используй spKDO_Aggregate group_by=week

3. spKDO_CommAgg — коммуникации (звонки, обзвоны)
   reason: all | outflow | leaving | forecast | noshow | quality | birthday | waitlist | opz
   group_by: reason | result | manager | list
   Примеры:
   - «коммуникации за неделю» → reason=all, group_by=reason
   - «результаты обзвона оттока» → reason=outflow, group_by=result
   - «менеджеры по звонкам» → reason=all, group_by=manager
   - «лист ожидания» → reason=waitlist, group_by=list
   - «ОПЗ» → reason=opz, group_by=list

ПАРАМЕТРЫ:
- date_from, date_to — ISO YYYY-MM-DD
- top — лимит строк (20)
- master_name — имя мастера если упомянуто

ПЕРИОДЫ:
- «за неделю» → 7 дней, «за месяц» → 30 дней, «за квартал» → 90 дней
- «за январь 2026» → 2026-01-01..2026-01-31
- Без периода → 30 дней. Сегодня: {today}

ВАЖНО:
- «отток по мастерам» = ClientList filter=outflow group_by=master
- «выручка по мастерам» = Aggregate group_by=master
- «тренд/динамика выручки по неделям» = Aggregate group_by=week
- «по неделям» → group_by=week, «по месяцам» → group_by=month (НЕ путай!)
- Абонементы/обучение — используй старые: dbo.spKDO_Attachments, dbo.spKDO_Training

КОНТЕКСТ ДИАЛОГА:
{context}
Если пользователь просит «сравни/покажи динамику» без уточнения темы — используй
предыдущую тему как ориентир. Например: предыдущая тема outflow + «сравни по месяцам»
→ spKDO_Aggregate group_by=month (сравнение KPI за период, привязанное к оттоку).

Ответь ТОЛЬКО JSON:
{{"procedure": "spKDO_Aggregate", "group_by": "total", "filter": "", "reason": "", "date_from": "YYYY-MM-DD", "date_to": "YYYY-MM-DD", "top": 20, "master_name": ""}}
"""

_JSON_RE = re.compile(r"\{[^{}]*\}", re.DOTALL)


def _extract_json(raw: str) -> str | None:
    """Извлекает внешний JSON-объект из ответа LLM (поддерживает вложенные {})."""
    start = raw.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(raw[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return raw[start : i + 1]
    return None


class LLMClient:
    """Клиент для Ollama-совместимого LLM API (модель задаётся в settings.ollama_model)."""

    def __init__(self, settings: Settings):
        self.settings = settings
        # Circuit breaker state для plan_aggregates
        self._cb_failures: int = 0
        self._cb_open_until: float = 0.0

    async def plan_query(
        self, question: str, today: str, last_topic: str = ""
    ) -> dict[str, Any] | None:
        """LLM-планировщик: определяет процедуру, group_by, filter из вопроса.

        Возвращает dict с ключами: procedure, group_by, filter, reason,
        date_from, date_to, top, master_name.
        Или None если LLM недоступен.
        """
        if not self.settings.ollama_api_key:
            return None

        if last_topic:
            context = (
                f"Предыдущая тема диалога: {last_topic}. "
                f"Пользователь может ссылаться на неё (сравни, покажи динамику, подробнее)."
            )
        else:
            context = "Нет предыдущего контекста — первый вопрос в диалоге."
        system = _PLANNER_SYSTEM_PROMPT.format(today=today, context=context)

        raw = await self._raw_chat(system, question)
        if not raw:
            return None

        return self._parse_plan_json(raw)

    async def plan_aggregates(
        self,
        question: str,
        catalog_prompt: str,
        semantic_prompt: str,
    ) -> dict | None:
        """T025: Одношаговое LLM-планирование с каталогом агрегатов.

        Возвращает распарсенный JSON-dict или None при ошибке/circuit breaker.
        Timeout: settings.llm_plan_timeout (5s).
        Circuit breaker: после threshold подряд неудач → None на cooldown секунд.
        """
        if not self.settings.ollama_api_key:
            return None

        # Проверяем circuit breaker
        now = time.monotonic()
        if self._cb_open_until > now:
            logger.warning(
                "LLM circuit breaker open: %.0fs remaining",
                self._cb_open_until - now,
            )
            return None

        system_prompt = (
            "Ты — планировщик аналитических запросов. "
            "Ниже — каталог доступных агрегатов и семантический каталог.\n\n"
            f"КАТАЛОГ АГРЕГАТОВ:\n{catalog_prompt}\n\n"
            f"СЕМАНТИЧЕСКИЙ КАТАЛОГ:\n{semantic_prompt}\n\n"
            "Пользователь задаёт вопрос на русском. "
            "Выбери подходящие агрегаты из каталога и верни JSON:\n"
            '{"intent": "single|comparison|decomposition|trend|ranking", '
            '"queries": [{"aggregate_id": "...", "params": {...}, "label": "..."}], '
            '"topic": "statistics", "render_needed": true}\n\n'
            "ПРАВИЛА DECOMPOSITION:\n"
            "Если вопрос содержит «почему», «из-за чего», «что повлияло», «причина» "
            "или аналогичные запросы на факторный анализ — используй intent=decomposition.\n"
            "При decomposition запроси ВСЕ связанные метрики за ДВА периода:\n"
            "Пример: «почему упала выручка?» → 5 запросов:\n"
            "  1. revenue_summary за текущий период\n"
            "  2. revenue_summary за предыдущий период\n"
            "  3. client_count за текущий период\n"
            "  4. client_count за предыдущий период\n"
            "  5. avg_check (один период достаточно)\n"
            "Максимум 5 запросов при decomposition. "
            "Ставь понятный label: «Выручка (апрель)», «Клиенты (март)» и т.д.\n\n"
            "ВАЖНО: используй только aggregate_id из каталога выше. "
            "Ответь ТОЛЬКО JSON, без пояснений."
        )

        base = self.settings.ollama_base_url.rstrip("/")
        url = f"{base}/chat"
        headers = {
            "Authorization": f"Bearer {self.settings.ollama_api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.settings.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
            "stream": False,
            "options": {"temperature": 0.1},
        }

        try:
            timeout = float(self.settings.llm_plan_timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.error("plan_aggregates request failed: %s", exc)
            self._cb_failures += 1
            if self._cb_failures >= self.settings.llm_circuit_breaker_threshold:
                cooldown = self.settings.llm_circuit_breaker_cooldown
                self._cb_open_until = time.monotonic() + cooldown
                logger.warning(
                    "LLM circuit breaker opened for %ds after %d consecutive failures",
                    cooldown,
                    self._cb_failures,
                )
            return None

        raw = self._extract_content(data)
        if not raw:
            self._cb_failures += 1
            return None

        result = self._parse_multiplan_json(raw)
        if result is not None:
            # Успех — сбрасываем счётчик ошибок
            self._cb_failures = 0
        return result

    def _parse_multiplan_json(self, raw: str) -> dict[str, Any] | None:
        """Извлекает JSON MultiPlan из ответа LLM (поддерживает вложенные объекты)."""
        json_str = _extract_json(raw)
        if not json_str:
            logger.warning("plan_aggregates returned no JSON: %s", raw[:200])
            return None
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("plan_aggregates returned invalid JSON: %s", raw[:200])
            return None

        if "queries" not in data:
            logger.warning("plan_aggregates JSON missing 'queries': %s", data)
            return None

        return data

    def _parse_plan_json(self, raw: str) -> dict[str, Any] | None:
        """Извлекает JSON из ответа LLM (может быть обёрнут в markdown)."""
        m = _JSON_RE.search(raw)
        if not m:
            logger.warning("LLM planner returned no JSON: %s", raw[:200])
            return None
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            logger.warning("LLM planner returned invalid JSON: %s", raw[:200])
            return None

        if "procedure" not in data:
            logger.warning("LLM planner JSON missing 'procedure': %s", data)
            return None

        return data

    async def _raw_chat(self, system_prompt: str, user_prompt: str) -> str:
        """Низкоуровневый вызов Ollama /api/chat, возвращает raw text."""
        base = self.settings.ollama_base_url.rstrip("/")
        url = f"{base}/chat"

        headers = {
            "Authorization": f"Bearer {self.settings.ollama_api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.settings.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.1},
        }

        try:
            timeout = float(getattr(self.settings, "llm_plan_timeout", 30))
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.error("LLM planner request failed: %s", exc)
            return ""

        return self._extract_content(data)

    async def synthesize(
        self, system_prompt: str, user_prompt: str, fallback_text: str
    ) -> str:
        if not self.settings.ollama_api_key:
            return fallback_text

        base = self.settings.ollama_base_url.rstrip("/")
        url = f"{base}/chat"

        headers = {
            "Authorization": f"Bearer {self.settings.ollama_api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.settings.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.error("LLM request failed: %s", exc)
            return fallback_text

        text = self._extract_content(data)
        return text or fallback_text

    @staticmethod
    def _extract_content(data: dict[str, Any]) -> str:
        """Извлекает текст ответа из Ollama /api/chat response."""
        message = data.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
        return ""
