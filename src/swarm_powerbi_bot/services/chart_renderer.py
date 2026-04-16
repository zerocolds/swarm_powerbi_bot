"""Рендеринг графиков из SQL-данных для отправки в Telegram.

Поддерживает: bar, horizontal bar, line, pie, table.
Автоматически выбирает тип графика по теме и данным.
"""
from __future__ import annotations

import io
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

    HAS_MPL = True
except ImportError:  # pragma: no cover
    HAS_MPL = False

# Русские шрифты: пробуем DejaVu Sans (есть в Docker)
if HAS_MPL:
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False

# ── Маппинг тем → предпочтительный тип графика ──────────────

_TOPIC_CHART: dict[str, str] = {
    "statistics": "bar",
    "trend": "line",
    "forecast": "hbar",
    "outflow": "hbar",
    "leaving": "hbar",
    "communications": "bar",
    "referrals": "pie",
    "quality": "bar",
    "masters": "hbar",
    "services": "hbar",
    "noshow": "hbar",
    "opz": "bar",
    "attachments": "bar",
    "training": "hbar",
    "all_clients": "bar",
    "birthday": "table_only",
    "waitlist": "table_only",
}


def choose_chart_type(topic: str, rows: list[dict[str, Any]]) -> str:
    """Выбирает тип графика по теме и данным."""
    return _TOPIC_CHART.get(topic, "bar")


def render_chart(
    topic: str,
    rows: list[dict[str, Any]],
    params: dict[str, Any],
    *,
    title: str = "",
) -> bytes | None:
    """Рендерит PNG-график из SQL-результата. Возвращает bytes или None."""
    if not HAS_MPL or not rows:
        return None

    chart_type = choose_chart_type(topic, rows)

    try:
        if chart_type == "table_only":
            return _render_table(rows, params, title)
        elif chart_type == "line":
            return _render_line(rows, params, title)
        elif chart_type == "pie":
            return _render_pie(rows, params, title)
        elif chart_type == "hbar":
            return _render_hbar(rows, params, title)
        else:
            return _render_bar(rows, params, title)
    except Exception:
        logger.exception("Chart render failed for topic=%s", topic)
        return None


def _period_label(params: dict[str, Any]) -> str:
    """Формирует подпись периода."""
    d_from = params.get("DateFrom")
    d_to = params.get("DateTo")
    if d_from and d_to:
        return f"{d_from} — {d_to}"
    return ""


def _auto_title(topic: str, params: dict[str, Any], override: str) -> str:
    if override:
        return override
    from .topic_registry import get_description
    desc = get_description(topic)
    period = _period_label(params)
    if period:
        return f"{desc}\n{period}"
    return desc


# Предпочтительная value-колонка по теме (что осмысленнее показывать)
_PREFERRED_VALUE: dict[str, str] = {
    "outflow": "TotalSpent",
    "leaving": "TotalSpent",
    "forecast": "TotalSpent",
    "noshow": "TotalVisits",
    "masters": "TotalRevenue",
    "services": "ServiceCount",
    "all_clients": "TotalVisits",
    "quality": "TotalVisits",
}


def _pick_label_value(
    rows: list[dict[str, Any]], topic: str = "",
) -> tuple[str, str]:
    """Автоматически выбирает колонку для подписей и значений."""
    if not rows:
        return "", ""
    keys = list(rows[0].keys())

    # Для подписей: первая текстовая колонка
    label_col = ""
    for k in keys:
        val = rows[0].get(k)
        if isinstance(val, str) and k not in ("SalonName", "Phone"):
            label_col = k
            break

    # Для значений: предпочтительная колонка по теме, иначе первая числовая
    value_col = ""
    preferred = _PREFERRED_VALUE.get(topic, "")
    if preferred and preferred in keys:
        val = rows[0].get(preferred)
        if isinstance(val, (int, float)):
            value_col = preferred

    if not value_col:
        # IsPrimary — булево поле, не подходит для value axis
        skip = {"ObjectId", "MasterId", "ClientId", "Id", "CRMId", "Top",
                "DaysSinceLastVisit", "DaysOverdue", "ServicePeriodDays", "IsPrimary"}
        for k in keys:
            val = rows[0].get(k)
            # bool является подклассом int в Python, явно исключаем
            if isinstance(val, (int, float)) and not isinstance(val, bool) and k not in skip:
                value_col = k
                break

    return label_col, value_col


def _pick_multi_values(rows: list[dict[str, Any]]) -> list[str]:
    """Для bar-графиков со статистикой: все числовые колонки (без bool)."""
    if not rows:
        return []
    skip = {"ObjectId", "MasterId", "ClientId", "Id", "CRMId", "Top"}
    return [
        k for k in rows[0].keys()
        if isinstance(rows[0].get(k), (int, float))
        and not isinstance(rows[0].get(k), bool)
        and k not in skip
    ]


def _format_number(n: float) -> str:
    """Форматирует числа для подписей: 1234567 → 1.2M, 12345 → 12.3K."""
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if abs(n) >= 10_000:
        return f"{n / 1_000:.1f}K"
    if isinstance(n, float) and n != int(n):
        return f"{n:.1f}"
    return str(int(n))


# ── Рендереры ────────────────────────────────────────────────

def _render_bar(rows: list[dict[str, Any]], params: dict[str, Any], title: str) -> bytes:
    """Вертикальная столбчатая диаграмма."""
    # Для Statistics: несколько метрик в одной строке
    if len(rows) == 1:
        return _render_single_row_bar(rows[0], params, title)

    label_col, value_col = _pick_label_value(rows, params.get("topic", ""))
    if not label_col or not value_col:
        return _render_single_row_bar(rows[0], params, title)

    labels = [str(r.get(label_col, ""))[:20] for r in rows[:15]]
    values = [float(r.get(value_col, 0) or 0) for r in rows[:15]]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(labels)), values, color="#4472C4")

    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                _format_number(v), ha="center", va="bottom", fontsize=8)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel(value_col)
    ax.set_title(_auto_title(params.get("topic", ""), params, title), fontsize=11)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: _format_number(x)))

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _render_single_row_bar(row: dict[str, Any], params: dict[str, Any], title: str) -> bytes:
    """Одна строка с несколькими метриками → группа столбцов."""
    skip = {"SalonName", "ObjectId", "MasterId", "ClientId", "Top"}
    metrics = {k: float(v) for k, v in row.items()
               if isinstance(v, (int, float)) and not isinstance(v, bool)
               and k not in skip and v}
    if not metrics:
        metrics = {"Нет данных": 0}

    labels = list(metrics.keys())[:10]
    values = list(metrics.values())[:10]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(labels)), values, color="#4472C4")

    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                _format_number(v), ha="center", va="bottom", fontsize=9)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_title(_auto_title(params.get("topic", ""), params, title), fontsize=11)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: _format_number(x)))

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _render_hbar(rows: list[dict[str, Any]], params: dict[str, Any], title: str) -> bytes:
    """Горизонтальная столбчатая диаграмма (для рейтингов/списков)."""
    label_col, value_col = _pick_label_value(rows, params.get("topic", ""))
    if not label_col or not value_col:
        if rows:
            return _render_single_row_bar(rows[0], params, title)
        return _empty_chart(params, title)

    labels = [str(r.get(label_col, ""))[:25] for r in rows[:15]]
    values = [float(r.get(value_col, 0) or 0) for r in rows[:15]]

    # Обратный порядок: самый большой сверху
    labels.reverse()
    values.reverse()

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.4)))
    bars = ax.barh(range(len(labels)), values, color="#4472C4")

    for bar, v in zip(bars, values):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
                f" {_format_number(v)}", ha="left", va="center", fontsize=9)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel(value_col)
    ax.set_title(_auto_title(params.get("topic", ""), params, title), fontsize=11)

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _render_line(rows: list[dict[str, Any]], params: dict[str, Any], title: str) -> bytes:
    """Линейный график (тренды)."""
    # Ищем временную колонку
    time_col = ""
    for k in ("WeekEnd", "MonthEnd", "DateFrom", "Date"):
        if k in rows[0]:
            time_col = k
            break

    value_cols = _pick_multi_values(rows)
    if not time_col or not value_cols:
        return _render_bar(rows, params, title)

    x_labels = [str(r.get(time_col, ""))[:10] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5"]

    for i, vc in enumerate(value_cols[:3]):
        values = [float(r.get(vc, 0) or 0) for r in rows]
        ax.plot(range(len(x_labels)), values, marker="o", markersize=4,
                label=vc, color=colors[i % len(colors)])

    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=8)
    ax.legend(fontsize=9)
    ax.set_title(_auto_title("trend", params, title), fontsize=11)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: _format_number(x)))
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _render_pie(rows: list[dict[str, Any]], params: dict[str, Any], title: str) -> bytes:
    """Круговая диаграмма (рефережи, каналы)."""
    label_col, value_col = _pick_label_value(rows, params.get("topic", ""))
    if not label_col or not value_col:
        return _render_bar(rows, params, title)

    data = [(str(r.get(label_col, ""))[:20], float(r.get(value_col, 0) or 0))
            for r in rows[:8]]
    data = [(lbl, val) for lbl, val in data if val > 0]

    if not data:
        return _empty_chart(params, title)

    labels, values = zip(*data)

    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.Set3.colors[:len(labels)]
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=140, textprops={"fontsize": 9},
    )
    ax.set_title(_auto_title(params.get("topic", ""), params, title), fontsize=11)

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _render_table(rows: list[dict[str, Any]], params: dict[str, Any], title: str) -> bytes:
    """Рендерит таблицу данных как PNG-картинку."""
    if not rows:
        return _empty_chart(params, title)

    # Убираем служебные колонки
    skip = {"CRMId", "ObjectId", "MasterId", "Top"}
    cols = [k for k in rows[0].keys() if k not in skip][:8]

    # Форматируем данные
    cell_data = []
    for r in rows[:15]:
        row_cells = []
        for c in cols:
            val = r.get(c, "")
            if val is None:
                val = "—"
            elif isinstance(val, float):
                val = _format_number(val)
            else:
                val = str(val)[:25]
            row_cells.append(val)
        cell_data.append(row_cells)

    # Укорачиваем заголовки
    col_labels = [c[:15] for c in cols]

    fig_height = max(2.5, 0.4 * len(cell_data) + 1.5)
    fig_width = max(8, len(cols) * 1.5)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("off")
    ax.set_title(_auto_title(params.get("topic", ""), params, title),
                 fontsize=11, pad=10)

    table = ax.table(
        cellText=cell_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.3)

    # Стилизация заголовков
    for j in range(len(cols)):
        cell = table[0, j]
        cell.set_facecolor("#4472C4")
        cell.set_text_props(color="white", fontweight="bold")

    # Чередование строк
    for i in range(1, len(cell_data) + 1):
        for j in range(len(cols)):
            if i % 2 == 0:
                table[i, j].set_facecolor("#D9E2F3")

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _empty_chart(params: dict[str, Any], title: str) -> bytes:
    """Пустой график с сообщением."""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.text(0.5, 0.5, "Нет данных для визуализации", ha="center", va="center",
            fontsize=14, color="gray")
    ax.axis("off")
    ax.set_title(title or "Нет данных", fontsize=11)
    fig.tight_layout()
    return _fig_to_bytes(fig)


def _fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# Маппинг group_by → колонка-метка в данных (ось X для per-row chart)
_GROUP_BY_LABEL_COL: dict[str, str] = {
    "status": "ClientStatus",
    "master": "MasterName",
    "reason": "Reason",
    "result": "Result",
    "manager": "Manager",
    "service": "ServiceName",
    "salon": "SalonName",
    "channel": "Channel",
}

# Предпочтительная value-колонка для per-row comparison
_GROUP_BY_VALUE_COL: dict[str, str] = {
    "status": "ClientCount",
    "master": "Revenue",
    "reason": "TotalCount",
    "result": "TotalCount",
    "manager": "TotalCount",
    "service": "Revenue",
    "salon": "Revenue",
    "channel": "ClientCount",
}


def render_comparison(
    topic: str,
    results_a: list[dict[str, Any]],
    results_b: list[dict[str, Any]],
    label_a: str,
    label_b: str,
    *,
    group_by: str = "",
) -> bytes:
    """Рендерит сгруппированный столбчатый график для сравнения двух периодов.

    Если group_by указан и label-колонка найдена в данных — per-row grouped bars
    (ось X = значения label-колонки, напр. статусы клиентов).
    Иначе — агрегация всех строк в одну сумму per metric (legacy поведение).
    """
    if not HAS_MPL:
        raise RuntimeError("matplotlib не установлен")

    # Пробуем per-row chart если group_by задан
    label_col = _GROUP_BY_LABEL_COL.get(group_by, "")
    if label_col and results_a and label_col in results_a[0]:
        return _render_comparison_per_row(
            results_a, results_b, label_a, label_b, label_col,
            _GROUP_BY_VALUE_COL.get(group_by, ""),
        )

    # Legacy: агрегация всех строк в одну сумму per metric
    return _render_comparison_aggregated(
        topic, results_a, results_b, label_a, label_b,
    )


def _render_comparison_per_row(
    results_a: list[dict[str, Any]],
    results_b: list[dict[str, Any]],
    label_a: str,
    label_b: str,
    label_col: str,
    value_col: str,
) -> bytes:
    """Per-row grouped bars: каждая строка = одна группа на оси X."""
    # Собираем данные: label → value для каждого набора
    def _row_map(rows: list[dict[str, Any]]) -> dict[str, float]:
        m: dict[str, float] = {}
        for row in rows:
            lbl = str(row.get(label_col, ""))[:25]
            if not lbl:
                continue
            # Ищем value: предпочтительная колонка или первая числовая
            val = row.get(value_col) if value_col else None
            if not isinstance(val, (int, float)):
                for v in row.values():
                    if isinstance(v, (int, float)):
                        val = v
                        break
            m[lbl] = float(val) if isinstance(val, (int, float)) else 0.0
        return m

    map_a = _row_map(results_a)
    map_b = _row_map(results_b)

    # Объединяем ключи (сохраняем порядок из A)
    all_labels = list(dict.fromkeys(list(map_a.keys()) + list(map_b.keys())))[:12]
    if not all_labels:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "Нет данных для сравнения",
                ha="center", va="center", fontsize=12, color="gray")
        ax.axis("off")
        fig.tight_layout()
        return _fig_to_bytes(fig)

    values_a = [map_a.get(lbl, 0.0) for lbl in all_labels]
    values_b = [map_b.get(lbl, 0.0) for lbl in all_labels]

    x = list(range(len(all_labels)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(8, len(all_labels) * 1.2), 6))

    bars_a = ax.bar([xi - width / 2 for xi in x], values_a, width=width,
                    label=label_a, color="#4472C4")
    bars_b = ax.bar([xi + width / 2 for xi in x], values_b, width=width,
                    label=label_b, color="#ED7D31")

    # Аннотации
    for bar, v in zip(bars_a, values_a):
        if v:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    _format_number(v), ha="center", va="bottom", fontsize=7, color="#4472C4")
    for bar, v in zip(bars_b, values_b):
        if v:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    _format_number(v), ha="center", va="bottom", fontsize=7, color="#ED7D31")

    # Дельты
    for i, (va, vb) in enumerate(zip(values_a, values_b)):
        if vb != 0:
            delta = (va - vb) / abs(vb) * 100
        elif va != 0:
            continue
        else:
            delta = 0.0
        top_val = max(va, vb)
        y_pos = top_val * 1.03 if top_val > 0 else 0.03
        if delta > 0:
            txt, clr = f"+{delta:.0f}%", "green"
        elif delta < 0:
            txt, clr = f"\u2212{abs(delta):.0f}%", "red"
        else:
            txt, clr = "0%", "gray"
        ax.text(i, y_pos, txt, ha="center", va="bottom", fontsize=8,
                color=clr, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(all_labels, rotation=30, ha="right", fontsize=9)
    ax.legend(fontsize=9)
    ax.set_title(f"Сравнение: {label_a} vs {label_b}", fontsize=11)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, _: _format_number(val)))
    ax.set_ylabel(value_col or "Значение")

    fig.tight_layout()
    return _fig_to_bytes(fig)


def _render_comparison_aggregated(
    topic: str,
    results_a: list[dict[str, Any]],
    results_b: list[dict[str, Any]],
    label_a: str,
    label_b: str,
) -> bytes:
    """Legacy: агрегация всех строк → одна сумма per metric → grouped bars по метрикам."""
    skip = {"ObjectId", "MasterId", "ClientId", "Id", "CRMId", "Top"}

    def _aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, float]:
        totals: dict[str, float] = {}
        for row in rows:
            for k, v in row.items():
                if isinstance(v, (int, float)) and k not in skip:
                    totals[k] = totals.get(k, 0.0) + float(v)
        return totals

    agg_a = _aggregate_rows(results_a) if results_a else {}
    agg_b = _aggregate_rows(results_b) if results_b else {}

    all_keys = list(dict.fromkeys(list(agg_a.keys()) + list(agg_b.keys())))
    if not all_keys:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "Нет числовых данных для сравнения",
                ha="center", va="center", fontsize=12, color="gray")
        ax.axis("off")
        ax.set_title(f"Сравнение: {label_a} vs {label_b}", fontsize=11)
        fig.tight_layout()
        return _fig_to_bytes(fig)

    all_keys = all_keys[:8]
    values_a = [agg_a.get(k, 0.0) for k in all_keys]
    values_b = [agg_b.get(k, 0.0) for k in all_keys]

    deltas: list[float | None] = []
    for va, vb in zip(values_a, values_b):
        if vb != 0:
            deltas.append((va - vb) / abs(vb) * 100)
        elif va != 0:
            deltas.append(None)
        else:
            deltas.append(0.0)

    x = list(range(len(all_keys)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(8, len(all_keys) * 1.5), 6))

    bars_a = ax.bar([xi - width / 2 for xi in x], values_a, width=width,
                    label=label_a, color="#4472C4")
    bars_b = ax.bar([xi + width / 2 for xi in x], values_b, width=width,
                    label=label_b, color="#ED7D31")

    for bar, v in zip(bars_a, values_a):
        if v:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    _format_number(v), ha="center", va="bottom", fontsize=7, color="#4472C4")
    for bar, v in zip(bars_b, values_b):
        if v:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    _format_number(v), ha="center", va="bottom", fontsize=7, color="#ED7D31")

    for i, (va, vb, delta) in enumerate(zip(values_a, values_b, deltas)):
        if delta is None:
            continue
        top_val = max(va, vb)
        y_pos = top_val * 1.03 if top_val > 0 else 0.03
        if delta > 0:
            txt, clr = f"+{delta:.1f}%", "green"
        elif delta < 0:
            txt, clr = f"\u2212{abs(delta):.1f}%", "red"
        else:
            txt, clr = "0%", "gray"
        ax.text(i, y_pos, txt, ha="center", va="bottom", fontsize=8,
                color=clr, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([k[:20] for k in all_keys], rotation=30, ha="right", fontsize=9)
    ax.legend(fontsize=9)
    ax.set_title(f"Сравнение: {label_a} vs {label_b}", fontsize=11)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, _: _format_number(val)))
    ax.set_ylabel("Значение")

    fig.tight_layout()
    return _fig_to_bytes(fig)
