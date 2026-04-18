# Data-Methods Inventory

Инвентаризация MSSQL-хранимок и атомарных data-method-обёрток.

> Обновлено: 2026-04-18. Основание: рефакторинг epic #12 (foundational task #13).

## Правила вызова

- Все методы принимают keyword-only аргументы `date_from: date, date_to: date`.
- `object_id: int | None` — ID салона (YClientsId). Обязателен для большинства методов; `revenue_by_salon` допускает `None` (сеть).
- `master_id: int | None` — опциональный фильтр по мастеру.
- `top: int = 20` — максимальное число строк (передаётся как `@Top`).
- Return type строго `pd.DataFrame`. Пустой результат → `DataFrame` с правильными колонками, не `raise`.
- Таймаут (`pyodbc.Error`) всплывает к вызывающему — не ловится на уровне data-methods.
- Множественные result-sets хранимки: берётся **первый** (единственный `cursor.fetchall()`).

## Таблица: хранимка → data-method

### spKDO_Aggregate

Параметр `@GroupBy` определяет режим агрегации.

| aggregate_id | data-method | @GroupBy | Возвращаемые колонки | Описание |
|---|---|---|---|---|
| `revenue_total` | `get_revenue_total` | `total` | Visits, UniqueClients, ActiveMasters, Revenue, AvgCheck, TotalHours, ReturningClients, SalonName | Сводные KPI за период (одна строка) |
| `revenue_by_week` | `get_revenue_by_week` | `week` | Period, Visits, UniqueClients, Revenue, AvgCheck, ActiveMasters | Недельный тренд |
| `revenue_by_month` | `get_revenue_by_month` | `month` | Period, Visits, UniqueClients, Revenue, AvgCheck, ActiveMasters | Помесячный тренд |
| `revenue_by_master` | `get_revenue_by_master` | `master` | MasterName, Rating, Visits, UniqueClients, Revenue, AvgCheck, TotalHours, RevenuePerHour, SalonName | Выручка и загрузка по мастерам |
| `revenue_by_service` | `get_revenue_by_service` | `service` | ServiceName, ServiceCategory, ServiceCount, UniqueClients, Revenue, AvgCheck, SalonName | Выручка по услугам |
| `revenue_by_salon` | `get_revenue_by_salon` | `salon` | SalonName, Visits, UniqueClients, ActiveMasters, Revenue, AvgCheck | Сравнение салонов (object_id необязателен) |
| `revenue_by_channel` | `get_revenue_by_channel` | `channel` | Channel, ClientCount, Visits, Revenue, AvgCheck, SalonName | Каналы привлечения |

### spKDO_ClientList

Параметр `@Filter` выбирает выборку клиентов.

| aggregate_id | data-method | @Filter | Возвращаемые колонки | Описание |
|---|---|---|---|---|
| `clients_outflow` | `get_clients_outflow` | `outflow` | ClientName, Phone, Category, ClientStatus, LastVisit, FirstVisit, ExpectedNextVisit, DaysSinceLastVisit, DaysOverdue, ServicePeriodDays, TotalVisits, TotalSpent, LastCommResult, SalonName | Клиенты в оттоке (31–240 дней просрочки) |
| `clients_leaving` | `get_clients_leaving` | `leaving` | ClientName, Phone, Category, ClientStatus, LastVisit, ExpectedNextVisit, DaysSinceLastVisit, DaysOverdue, ServicePeriodDays, TotalVisits, TotalSpent, LastCommResult, SalonName | Уходящие клиенты (1–30 дней просрочки) |
| `clients_forecast` | `get_clients_forecast` | `forecast` | ClientName, Phone, Category, ClientStatus, LastVisit, ExpectedNextVisit, DaysUntilExpected, ServicePeriodDays, TotalVisits, TotalSpent, LastCommResult, SalonName | Прогноз визитов (0–14 дней) |
| `clients_noshow` | `get_clients_noshow` | `noshow` | ClientName, Phone, Category, ClientStatus, LastCancelledVisit, LastSuccessVisit, FirstVisit, LastCommResult, LastCommDate, SalonName | Недошедшие клиенты |
| `clients_quality` | `get_clients_quality` | `quality` | ClientName, Phone, Category, ClientStatus, LastVisit, FirstVisit, ExpectedNextVisit, TotalVisits, TotalSpent, LastCommResult, SalonName | Контроль качества (визит ≤ 7 дней) |
| `clients_birthday` | `get_clients_birthday` | `birthday` | ClientName, Phone, BirthDate, Age, Category, SalonName, Congratulated | Именинники в диапазон дат |
| `clients_all` | `get_clients_all` | `all` | ClientName, Phone, Category, ClientStatus, LastVisit, FirstVisit, ExpectedNextVisit, DaysSinceLastVisit, DaysOverdue, ServicePeriodDays, TotalVisits, TotalSpent, LastCommResult, SalonName | Полная клиентская база |

### spKDO_CommAgg

Параметры `@Reason` + `@GroupBy` определяют фильтрацию и агрегацию.

| aggregate_id | data-method | @Reason | @GroupBy | Возвращаемые колонки | Описание |
|---|---|---|---|---|---|
| `comm_all_by_reason` | `get_comm_all_by_reason` | `all` | `reason` | Reason, TotalCount, UniqueClients, BookedCount, RefusedCount, SalonName | Все коммуникации по типам причин |
| `comm_all_by_result` | `get_comm_all_by_result` | `all` | `result` | Result, TotalCount, UniqueClients, SalonName | Все коммуникации по результату |
| `comm_all_by_manager` | `get_comm_all_by_manager` | `all` | `manager` | Manager, TotalCount, UniqueClients, BookedCount, SalonName | Все коммуникации по менеджерам |
| `comm_all_list` | `get_comm_all_list` | `all` | `list` | CommDate, Reason, CommType, Result, Manager, ClientPhone, ClientCategory, Comment, SalonName | Детальный список коммуникаций |
| `comm_outflow_by_reason` | `get_comm_outflow_by_reason` | `outflow` | `reason` | Reason, TotalCount, UniqueClients, BookedCount, RefusedCount, SalonName | Коммуникации по оттоку |
| `comm_leaving_by_result` | `get_comm_leaving_by_result` | `leaving` | `result` | Result, TotalCount, UniqueClients, SalonName | Коммуникации по уходящим |
| `comm_forecast_by_result` | `get_comm_forecast_by_result` | `forecast` | `result` | Result, TotalCount, UniqueClients, SalonName | Коммуникации по прогнозу визитов |
| `comm_noshow_by_manager` | `get_comm_noshow_by_manager` | `noshow` | `manager` | Manager, TotalCount, UniqueClients, BookedCount, SalonName | Коммуникации по недошедшим |
| `comm_quality_by_result` | `get_comm_quality_by_result` | `quality` | `result` | Result, TotalCount, UniqueClients, SalonName | Результаты контроля качества |
| `comm_birthday_by_result` | `get_comm_birthday_by_result` | `birthday` | `result` | Result, TotalCount, UniqueClients, SalonName | Поздравления с ДР |
| `comm_waitlist_by_manager` | `get_comm_waitlist_by_manager` | `waitlist` | `manager` | Manager, TotalCount, UniqueClients, BookedCount, SalonName | Лист ожидания |
| `comm_opz_by_result` | `get_comm_opz_by_result` | `opz` | `result` | Result, TotalCount, UniqueClients, SalonName | ОПЗ — оперативная запись |

### Legacy-процедуры (не в DATA_METHODS)

Следующие хранимки вызываются из `_fetch_rows_sync` / `_fetch_with_query_params` и не имеют
catalog-backed data-methods. Они остаются как legacy fallback и планируются к обёртке в #14.

| Процедура | Topic | Примечание |
|---|---|---|
| `spKDO_Attachments` | `attachments` | Абонементы |
| `spKDO_Training` | `training` | Обучение мастеров |
| `spKDO_Statistics` (v1) | `statistics` | Обратная совместимость, маппится на `revenue_total` |
| `spKDO_Trend` (v1) | `trend` | Маппится на `revenue_by_week` / `revenue_by_month` |
| `spKDO_Outflow` (v1) | `outflow` | Маппится на `clients_outflow` |
| `spKDO_Leaving` (v1) | `leaving` | Маппится на `clients_leaving` |
| `spKDO_Forecast` (v1) | `forecast` | Маппится на `clients_forecast` |
| `spKDO_Masters` (v1) | `masters` | Маппится на `revenue_by_master` |
| `spKDO_Services` (v1) | `services` | Маппится на `revenue_by_service` |
| `spKDO_Communications` (v1) | `communications` | Маппится на `comm_all_by_reason` |
| `spKDO_Referrals` (v1) | `referrals` | Маппится на `revenue_by_channel` |
| `spKDO_Quality` (v1) | `quality` | Маппится на `clients_quality` |
| `spKDO_NoShow` (v1) | `noshow` | Маппится на `clients_noshow` |
| `spKDO_AllClients` (v1) | `all_clients` | Маппится на `clients_all` |
| `spKDO_Birthday` (v1) | `birthday` | Маппится на `clients_birthday` |
| `spKDO_WaitList` (v1) | `waitlist` | Маппится на `comm_waitlist_by_manager` |
| `spKDO_OPZ` (v1) | `opz` | Маппится на `comm_opz_by_result` |

## Edge cases

| Ситуация | Поведение |
|---|---|
| Хранимка без параметров даты | Метод принимает `date_from/date_to` как required, передаёт в `@DateFrom/@DateTo` |
| Хранимка возвращает >1 result set | Берётся **первый** (`cursor.fetchall()` без `cursor.nextset()`) |
| Таймаут MSSQL | `pyodbc.Error` всплывает к вызывающему (SQL-агент/композер) — не ловится |
| Пустой результат | Возвращается `DataFrame` с корректными колонками, `len() == 0` |
| `object_id=None` при salon-wide | `revenue_by_salon` допускает `None`; остальные вернут пустой DF без вызова MSSQL |
| Невалидное имя процедуры | `_execute_sp` отклоняет через `re.fullmatch` — возвращает пустой DF, не raise |
| `conn_str=""` | Возвращает пустой DF с правильными колонками |

## Зависимости

- `pyodbc>=5.1.0` — уже в `pyproject.toml`
- `pandas>=2.0` — добавлено в `pyproject.toml` в рамках данного рефакторинга
