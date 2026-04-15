"""Регистрация/подписка пользователей через spSubscribeToDigest."""
from __future__ import annotations

import asyncio
from urllib.parse import unquote_plus

from ..config import Settings

try:
    import pyodbc  # type: ignore
except Exception:  # pragma: no cover
    pyodbc = None


def parse_start_arg(arg: str) -> tuple[int, str]:
    """Разбирает activation link: <customer_id>-<dataset_id>."""
    raw = unquote_plus(arg or "").strip()
    if not raw:
        raise ValueError(
            "Учётная запись не активирована. "
            "Для активации обратитесь в поддержку: https://t.me/kpi_bi"
        )

    try:
        cust_str, dataset_id = raw.split("-", 1)
    except ValueError:
        raise ValueError(
            "Ссылка активации некорректна. "
            "Обратитесь в поддержку: https://t.me/kpi_bi"
        )

    cust_str = cust_str.strip()
    dataset_id = dataset_id.strip()
    if not cust_str or not dataset_id:
        raise ValueError("Ошибка в параметрах активации. Обратитесь в поддержку.")

    try:
        customer_id = int(cust_str)
    except Exception:
        raise ValueError("Ошибка в параметре customerId. Обратитесь в поддержку.")

    if len(dataset_id) < 8:
        raise ValueError("Ошибка в параметре datasetId. Обратитесь в поддержку.")

    return customer_id, dataset_id


def _subscribe_sync(
    customer_id: int,
    dataset_id: str,
    account_id: str,
    settings: Settings,
) -> tuple[int, str]:
    conn_str = settings.sql_connection_string()
    if not conn_str or pyodbc is None:
        return -500, "БД не настроена."

    with pyodbc.connect(conn_str, autocommit=False, timeout=10) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            DECLARE @retValue INT;
            EXEC @retValue = dbo.spSubscribeToDigest
                @pCustomerId=?, @pDatasetId=?, @pAccountId=?, @pAccountType=?;
            SELECT @retValue AS ret;
            """,
            (customer_id, dataset_id, account_id, "Telegram"),
        )
        row = cur.fetchone()
        code = int(row.ret) if row and getattr(row, "ret", None) is not None else -999

    if code == 200:
        return 200, "Подписка оформлена!"
    if code == -1:
        return -1, "Вы уже подписаны."
    return code, f"Ошибка подписки (код {code})"


async def subscribe(
    customer_id: int,
    dataset_id: str,
    account_id: str,
    settings: Settings,
) -> tuple[int, str]:
    return await asyncio.to_thread(
        _subscribe_sync, customer_id, dataset_id, account_id, settings,
    )


def _is_subscribed_sync(account_id: str, settings: Settings) -> bool:
    conn_str = settings.sql_connection_string()
    if not conn_str or pyodbc is None:
        return False

    with pyodbc.connect(conn_str, autocommit=True, timeout=10) as conn:
        cur = conn.cursor()
        cur.execute("EXEC dbo.spGetSubscribers;")
        cols = [desc[0].lower() for desc in (cur.description or [])]
        for row in cur.fetchall():
            row_dict = dict(zip(cols, row))
            acct = str(row_dict.get("account", row_dict.get("accountid", row_dict.get("chatid", "")))).strip()
            acct_type = str(row_dict.get("type", row_dict.get("accounttype", ""))).strip().lower()
            if acct == account_id and "telegram" in acct_type:
                return True
    return False


async def is_subscribed(account_id: str, settings: Settings) -> bool:
    return await asyncio.to_thread(_is_subscribed_sync, account_id, settings)


def _get_user_object_id_sync(account_id: str, settings: Settings) -> int | None:
    """Получает ObjectId (SalonId) для пользователя через подписку.

    Цепочка: Account → DatasetId (из spGetSubscribers) → SalonId (из tbDatasetItems).
    """
    conn_str = settings.sql_connection_string()
    if not conn_str or pyodbc is None:
        return None

    with pyodbc.connect(conn_str, autocommit=True, timeout=10) as conn:
        cur = conn.cursor()

        # 1. Находим DatasetId пользователя
        cur.execute("EXEC dbo.spGetSubscribers;")
        cols = [desc[0].lower() for desc in (cur.description or [])]
        dataset_id = None
        for row in cur.fetchall():
            row_dict = dict(zip(cols, row))
            acct = str(row_dict.get("account", row_dict.get("accountid", ""))).strip()
            acct_type = str(row_dict.get("type", row_dict.get("accounttype", ""))).strip().lower()
            if acct == account_id and "telegram" in acct_type:
                dataset_id = row_dict.get("datasetid")
                break

        if not dataset_id:
            return None

        # 2. Маппим DatasetId → SalonId через tbDatasetItems
        cur.execute(
            "SELECT TOP 1 SalonId FROM tbDatasetItems WHERE DatasetId = ?",
            (str(dataset_id),),
        )
        row = cur.fetchone()
        return int(row[0]) if row else None


async def get_user_object_id(account_id: str, settings: Settings) -> int | None:
    """Асинхронно получает ObjectId (SalonId) для пользователя."""
    return await asyncio.to_thread(_get_user_object_id_sync, account_id, settings)
