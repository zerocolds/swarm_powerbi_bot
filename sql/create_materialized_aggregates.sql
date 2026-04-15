-- =====================================================
-- Материализованные агрегаты КДО (Indexed Views)
-- Phase 5: SQL Layer — T019
--
-- 4 индексированных представления для наиболее частых
-- шаблонов агрегации по tbRecords:
--   vwKDO_RevenueSummary  — выручка по дате + салону
--   vwKDO_MasterSummary   — выручка по дате + салону + мастеру
--   vwKDO_ServiceSummary  — выручка по дате + салону + услуге
--   vwKDO_ChannelSummary  — распределение по каналу + салону
--
-- Требования SQL Server indexed views:
--   - WITH SCHEMABINDING (нет SELECT *, нет подзапросов)
--   - COUNT_BIG(*) обязателен при наличии GROUP BY
--   - UNIQUE CLUSTERED INDEX на детерминированных столбцах
--   - Нет LEFT/RIGHT JOIN, нет DISTINCT, нет TOP
--   - Ссылки на таблицы — двухчастные имена (dbo.tbRecords)
-- =====================================================

-- ═══════════════════════════════════════════════════
-- 1. vwKDO_RevenueSummary
--    Дневная выручка по салону
--    Источник: Status=1, группировка по дате + ObjectId
-- ═══════════════════════════════════════════════════
IF EXISTS (
    SELECT 1 FROM sys.indexes i
    JOIN sys.objects o ON i.object_id = o.object_id
    WHERE o.name = 'vwKDO_RevenueSummary' AND i.name = 'UX_vwKDO_RevenueSummary'
)
    DROP INDEX UX_vwKDO_RevenueSummary ON dbo.vwKDO_RevenueSummary;
GO

IF OBJECT_ID('dbo.vwKDO_RevenueSummary', 'V') IS NOT NULL
    DROP VIEW dbo.vwKDO_RevenueSummary;
GO

CREATE VIEW dbo.vwKDO_RevenueSummary
WITH SCHEMABINDING
AS
    SELECT
        r.YClientsId                    AS ObjectId,
        CAST(r.DateOfAppointment AS DATE) AS AppointmentDate,
        SUM(r.AmountAC)                 AS TotalRevenue,
        COUNT_BIG(*)                    AS RecordCount
    FROM dbo.tbRecords r
    WHERE r.Status = 1
    GROUP BY
        r.YClientsId,
        CAST(r.DateOfAppointment AS DATE);
GO

CREATE UNIQUE CLUSTERED INDEX UX_vwKDO_RevenueSummary
    ON dbo.vwKDO_RevenueSummary (ObjectId, AppointmentDate);
GO


-- ═══════════════════════════════════════════════════
-- 2. vwKDO_MasterSummary
--    Дневная выручка по салону + мастеру
--    Источник: Status=1, группировка по дате + ObjectId + MasterId
-- ═══════════════════════════════════════════════════
IF EXISTS (
    SELECT 1 FROM sys.indexes i
    JOIN sys.objects o ON i.object_id = o.object_id
    WHERE o.name = 'vwKDO_MasterSummary' AND i.name = 'UX_vwKDO_MasterSummary'
)
    DROP INDEX UX_vwKDO_MasterSummary ON dbo.vwKDO_MasterSummary;
GO

IF OBJECT_ID('dbo.vwKDO_MasterSummary', 'V') IS NOT NULL
    DROP VIEW dbo.vwKDO_MasterSummary;
GO

CREATE VIEW dbo.vwKDO_MasterSummary
WITH SCHEMABINDING
AS
    SELECT
        r.YClientsId                    AS ObjectId,
        r.MasterId,
        CAST(r.DateOfAppointment AS DATE) AS AppointmentDate,
        SUM(r.AmountAC)                 AS TotalRevenue,
        COUNT_BIG(*)                    AS RecordCount
    FROM dbo.tbRecords r
    WHERE r.Status = 1
    GROUP BY
        r.YClientsId,
        r.MasterId,
        CAST(r.DateOfAppointment AS DATE);
GO

CREATE UNIQUE CLUSTERED INDEX UX_vwKDO_MasterSummary
    ON dbo.vwKDO_MasterSummary (ObjectId, MasterId, AppointmentDate);
GO


-- ═══════════════════════════════════════════════════
-- 3. vwKDO_ServiceSummary
--    Дневная выручка по салону + услуге
--    Источник: Status=1, группировка по дате + ObjectId + ServiceId
-- ═══════════════════════════════════════════════════
IF EXISTS (
    SELECT 1 FROM sys.indexes i
    JOIN sys.objects o ON i.object_id = o.object_id
    WHERE o.name = 'vwKDO_ServiceSummary' AND i.name = 'UX_vwKDO_ServiceSummary'
)
    DROP INDEX UX_vwKDO_ServiceSummary ON dbo.vwKDO_ServiceSummary;
GO

IF OBJECT_ID('dbo.vwKDO_ServiceSummary', 'V') IS NOT NULL
    DROP VIEW dbo.vwKDO_ServiceSummary;
GO

CREATE VIEW dbo.vwKDO_ServiceSummary
WITH SCHEMABINDING
AS
    SELECT
        r.YClientsId                    AS ObjectId,
        r.ServiceId,
        CAST(r.DateOfAppointment AS DATE) AS AppointmentDate,
        SUM(r.AmountAC)                 AS TotalRevenue,
        COUNT_BIG(*)                    AS RecordCount
    FROM dbo.tbRecords r
    WHERE r.Status = 1
    GROUP BY
        r.YClientsId,
        r.ServiceId,
        CAST(r.DateOfAppointment AS DATE);
GO

CREATE UNIQUE CLUSTERED INDEX UX_vwKDO_ServiceSummary
    ON dbo.vwKDO_ServiceSummary (ObjectId, ServiceId, AppointmentDate);
GO


-- ═══════════════════════════════════════════════════
-- 4. vwKDO_ChannelSummary
--    Распределение записей по каналу привлечения + салону
--    Источник: Status=1, группировка по ObjectId + Channel
--
--    Примечание: Channel = tbRecords.Channel (канал источника записи,
--    отличается от AcquisitionChannel в tbClients).
--    Indexed view не допускает JOIN с tbClients — отдельная view
--    для быстрой агрегации канала непосредственно из tbRecords.
-- ═══════════════════════════════════════════════════
IF EXISTS (
    SELECT 1 FROM sys.indexes i
    JOIN sys.objects o ON i.object_id = o.object_id
    WHERE o.name = 'vwKDO_ChannelSummary' AND i.name = 'UX_vwKDO_ChannelSummary'
)
    DROP INDEX UX_vwKDO_ChannelSummary ON dbo.vwKDO_ChannelSummary;
GO

IF OBJECT_ID('dbo.vwKDO_ChannelSummary', 'V') IS NOT NULL
    DROP VIEW dbo.vwKDO_ChannelSummary;
GO

CREATE VIEW dbo.vwKDO_ChannelSummary
WITH SCHEMABINDING
AS
    SELECT
        r.YClientsId                    AS ObjectId,
        r.Channel,
        CAST(r.DateOfAppointment AS DATE) AS AppointmentDate,
        COUNT_BIG(*)                    AS RecordCount
    FROM dbo.tbRecords r
    WHERE r.Status = 1
    GROUP BY
        r.YClientsId,
        r.Channel,
        CAST(r.DateOfAppointment AS DATE);
GO

CREATE UNIQUE CLUSTERED INDEX UX_vwKDO_ChannelSummary
    ON dbo.vwKDO_ChannelSummary (ObjectId, Channel, AppointmentDate);
GO
