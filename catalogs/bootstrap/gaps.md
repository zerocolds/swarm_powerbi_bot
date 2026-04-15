# DAX Gap Report — Not-Covered Measures

**Source mapping:** `catalogs/bootstrap/pbix-to-sql-mapping.yaml`

## Summary

| Classification       | Count | Share |
|----------------------|------:|------:|
| sql_covered          |     0 |   0.0% |
| python_postprocess   |     0 |   0.0% |
| **not_covered**      | **63** | **100.0%** |
| Total measures       |    63 |       |

### Priority breakdown (not_covered only)

- **P1**: 0 measure(s)
- **P2**: 3 measure(s)
- **P3**: 60 measure(s)

## Gaps by Source PBIX Table

### Абонементы

| Priority | Measure Name | Expression Preview |
|----------|:-------------|:-------------------|
| `P3` | Абонементы. miniCRM. AddNewItemURL | `(extracted from visual config)` |
| `P3` | Абонементы. miniCRM. YCClientProfileURL | `(extracted from visual config)` |
| `P3` | Абонементы. Заголовок таблицы | `(extracted from visual config)` |

### Константы

| Priority | Measure Name | Expression Preview |
|----------|:-------------|:-------------------|
| `P3` | miniCRM. AddNewItemURL | `(extracted from visual config)` |
| `P3` | miniCRM. YCClientProfileURL | `(extracted from visual config)` |
| `P3` | Безопасность. ReportUserId | `(extracted from visual config)` |
| `P3` | Отчет. Версия | `(extracted from visual config)` |
| `P3` | Отчет. Заголовок | `(extracted from visual config)` |
| `P3` | Трекинг. URL | `(extracted from visual config)` |

### Расчеты

| Priority | Measure Name | Expression Preview |
|----------|:-------------|:-------------------|
| `P2` | КДО. Оперативный визит. Мастер | `(extracted from visual config)` |
| `P2` | КДО. Последний несостоявшийся визит. Мастер | `(extracted from visual config)` |
| `P2` | КДО. Последний состоявшийся визит. Мастер | `(extracted from visual config)` |
| `P3` | Абонементы. Задолженность | `(extracted from visual config)` |
| `P3` | Абонементы. Количество | `(extracted from visual config)` |
| `P3` | Абонементы. Количество (действующих без нулевого остатка) | `(extracted from visual config)` |
| `P3` | Абонементы. Количество клиентов | `(extracted from visual config)` |
| `P3` | Абонементы. Количество оставшихся сеансов | `(extracted from visual config)` |
| `P3` | Абонементы. Состояние | `(extracted from visual config)` |
| `P3` | Возвращаемость | `(extracted from visual config)` |
| `P3` | КДО. Дата последней несостоявшейся записи (дата) | `(extracted from visual config)` |
| `P3` | КДО. Дата последней несостоявшейся записи (текст) | `(extracted from visual config)` |
| `P3` | КДО. Дата последней несостоявшейся записи (число) | `(extracted from visual config)` |
| `P3` | КДО. День рождения (дата) | `(extracted from visual config)` |
| `P3` | КДО. День рождения (текст) | `(extracted from visual config)` |
| `P3` | КДО. День рождения (число) | `(extracted from visual config)` |
| `P3` | КДО. Имя | `(extracted from visual config)` |
| `P3` | КДО. Категория клиента | `(extracted from visual config)` |
| `P3` | КДО. Количество визитов | `(extracted from visual config)` |
| `P3` | КДО. Ожидаемая дата (текст) | `(extracted from visual config)` |
| `P3` | КДО. Ожидаемая дата (число) | `(extracted from visual config)` |
| `P3` | КДО. Ожидаемая дата следуюшего визита (дата) | `(extracted from visual config)` |
| `P3` | КДО. Ожидается к мастеру | `(extracted from visual config)` |
| `P3` | КДО. Ожидается на услугу (Название) | `(extracted from visual config)` |
| `P3` | КДО. Оперативный визит. Дата | `(extracted from visual config)` |
| `P3` | КДО. Оперативный визит. Услуга | `(extracted from visual config)` |
| `P3` | КДО. Первый визит (дата) | `(extracted from visual config)` |
| `P3` | КДО. Последний визит (дата) | `(extracted from visual config)` |
| `P3` | КДО. Последний визит (текст) | `(extracted from visual config)` |
| `P3` | КДО. Последний визит (число) | `(extracted from visual config)` |
| `P3` | КДО. Последний несостоявшийся визит. Услуга (Название) | `(extracted from visual config)` |
| `P3` | КДО. Последний состоявшийся визит. Услуга (Название) | `(extracted from visual config)` |
| `P3` | КДО. Признак первого посещения выбранной категории услуг | `(extracted from visual config)` |
| `P3` | КДО. Признак что ближайшая будущая запись на любую категорию  сегодня | `(extracted from visual config)` |
| `P3` | КДО. Прошло дней с последнего визита | `(extracted from visual config)` |
| `P3` | КДО. Средний чек (услуги) | `(extracted from visual config)` |
| `P3` | КДО. Телефон | `(extracted from visual config)` |
| `P3` | КДО. Траты (услуги) | `(extracted from visual config)` |
| `P3` | КДО. Частота визитов | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. %  Довольных | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. %  Недовольных | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Количество визитов (all) | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Количество визитов (interval) | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Количество комммуникаций | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Количество созданных записей (interval) | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Количество уникальных клиентов с состоявшимися визитами после коммуникации | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Конверсия в визиты (interval) | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Конверсия в записи (interval) | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Последняя сводка | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Последняя сводка (абонеменеты) | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Сумма визитов (all) | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Сумма визитов (interval) | `(extracted from visual config)` |
| `P3` | Коммуникации с клиентами. Услуги на которые вернулись (interval) | `(extracted from visual config)` |

### Таблицы. Клиенты для обработки

| Priority | Measure Name | Expression Preview |
|----------|:-------------|:-------------------|
| `P3` | Статус клиента для обработки | `(extracted from visual config)` |

## P2 — important (client / клиент / master / мастер)

- **КДО. Оперативный визит. Мастер** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Последний несостоявшийся визит. Мастер** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Последний состоявшийся визит. Мастер** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```

## P3 — nice-to-have

- **Абонементы. miniCRM. AddNewItemURL** _(table: Абонементы)_
  ```
  (extracted from visual config)
  ```
- **Абонементы. miniCRM. YCClientProfileURL** _(table: Абонементы)_
  ```
  (extracted from visual config)
  ```
- **Абонементы. Заголовок таблицы** _(table: Абонементы)_
  ```
  (extracted from visual config)
  ```
- **miniCRM. AddNewItemURL** _(table: Константы)_
  ```
  (extracted from visual config)
  ```
- **miniCRM. YCClientProfileURL** _(table: Константы)_
  ```
  (extracted from visual config)
  ```
- **Безопасность. ReportUserId** _(table: Константы)_
  ```
  (extracted from visual config)
  ```
- **Отчет. Версия** _(table: Константы)_
  ```
  (extracted from visual config)
  ```
- **Отчет. Заголовок** _(table: Константы)_
  ```
  (extracted from visual config)
  ```
- **Трекинг. URL** _(table: Константы)_
  ```
  (extracted from visual config)
  ```
- **Абонементы. Задолженность** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Абонементы. Количество** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Абонементы. Количество (действующих без нулевого остатка)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Абонементы. Количество клиентов** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Абонементы. Количество оставшихся сеансов** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Абонементы. Состояние** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Возвращаемость** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Дата последней несостоявшейся записи (дата)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Дата последней несостоявшейся записи (текст)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Дата последней несостоявшейся записи (число)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. День рождения (дата)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. День рождения (текст)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. День рождения (число)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Имя** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Категория клиента** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Количество визитов** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Ожидаемая дата (текст)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Ожидаемая дата (число)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Ожидаемая дата следуюшего визита (дата)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Ожидается к мастеру** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Ожидается на услугу (Название)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Оперативный визит. Дата** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Оперативный визит. Услуга** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Первый визит (дата)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Последний визит (дата)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Последний визит (текст)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Последний визит (число)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Последний несостоявшийся визит. Услуга (Название)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Последний состоявшийся визит. Услуга (Название)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Признак первого посещения выбранной категории услуг** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Признак что ближайшая будущая запись на любую категорию  сегодня** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Прошло дней с последнего визита** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Средний чек (услуги)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Телефон** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Траты (услуги)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **КДО. Частота визитов** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. %  Довольных** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. %  Недовольных** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Количество визитов (all)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Количество визитов (interval)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Количество комммуникаций** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Количество созданных записей (interval)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Количество уникальных клиентов с состоявшимися визитами после коммуникации** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Конверсия в визиты (interval)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Конверсия в записи (interval)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Последняя сводка** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Последняя сводка (абонеменеты)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Сумма визитов (all)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Сумма визитов (interval)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Коммуникации с клиентами. Услуги на которые вернулись (interval)** _(table: Расчеты)_
  ```
  (extracted from visual config)
  ```
- **Статус клиента для обработки** _(table: Таблицы. Клиенты для обработки)_
  ```
  (extracted from visual config)
  ```
