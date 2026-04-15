-- =====================================================
-- TVF для динамической агрегации с фильтрацией
-- Phase 5: SQL Layer — T020
--
-- fnKDO_GapAggregate(@ObjectId, @DateFrom, @DateTo, @GroupBy, @Filter)
--
-- Назначение: покрывает «зазоры» между universal procedures —
-- комбинации @GroupBy + @Filter, не поддерживаемые spKDO_Aggregate.
--
-- Маршрутизация по @GroupBy:
--   master  — агрегация по мастерам (как в spKDO_Aggregate)
--   service — агрегация по услугам
--   salon   — агрегация по салонам
--   channel — агрегация по каналу (из tbRecords.Channel)
--   week    — по неделям (EndOfWeek)
--   month   — по месяцам (EndOfMonth)
--   total   — единственная строка KPI
--
-- @Filter (опциональный, по умолчанию 'all'):
--   all     — все записи со Status=1
--   primary — только первичные записи клиента
--   repeat  — только повторные записи
--
-- Отличие от spKDO_Aggregate:
--   TVF возвращает результат через RETURN TABLE — пригоден
--   для JOIN/CROSS APPLY в более сложных запросах.
--   Поддерживает фильтр primary/repeat без коррелированных
--   подзапросов (LEFT JOIN на MIN визита клиента).
-- =====================================================

IF OBJECT_ID('dbo.fnKDO_GapAggregate', 'TF') IS NOT NULL
    DROP FUNCTION dbo.fnKDO_GapAggregate;
GO

CREATE FUNCTION dbo.fnKDO_GapAggregate(
    @ObjectId  INT,
    @DateFrom  DATE,
    @DateTo    DATE,
    @GroupBy   VARCHAR(20),
    @Filter    VARCHAR(50)
)
RETURNS @Result TABLE
(
    -- Общие измерения (заполняется в зависимости от @GroupBy)
    GroupKey       NVARCHAR(200) NULL,  -- MasterName / ServiceName / SalonName / Channel / Period
    GroupId        INT           NULL,  -- MasterId / ServiceId / ObjectId (для числовых ключей)

    -- Метрики — одинаковы для всех GroupBy
    Visits         INT           NOT NULL,
    UniqueClients  INT           NOT NULL,
    TotalRevenue   DECIMAL(18,2) NOT NULL,
    AvgCheck       DECIMAL(18,2) NOT NULL,

    -- Дополнительные метрики (NULL когда неприменимы)
    ActiveMasters  INT           NULL,  -- для total / salon
    TotalHours     DECIMAL(10,2) NULL,  -- для master / total
    RevenuePerHour DECIMAL(18,2) NULL,  -- для master

    -- Контекст
    ObjectId       INT           NOT NULL,
    DateFrom       DATE          NOT NULL,
    DateTo         DATE          NOT NULL
)
AS
BEGIN
    -- ── Общая CTE: базовая выборка с учётом @Filter ────────────────
    -- primary: клиент появляется впервые (DateOfAppointment = минимальный Status=1)
    -- repeat:  клиент уже бывал ранее
    -- all:     без ограничений

    DECLARE @From DATE = ISNULL(@DateFrom, DATEADD(DAY, -30, GETDATE()));
    DECLARE @To   DATE = ISNULL(@DateTo,   GETDATE());

    -- ── master ──────────────────────────────────────────────────────
    IF @GroupBy = 'master'
    BEGIN
        INSERT INTO @Result
            (GroupKey, GroupId, Visits, UniqueClients, TotalRevenue, AvgCheck,
             TotalHours, RevenuePerHour, ObjectId, DateFrom, DateTo)
        SELECT
            m.Name                                    AS GroupKey,
            r.MasterId                                AS GroupId,
            COUNT(*)                                  AS Visits,
            COUNT(DISTINCT r.ClientId)                AS UniqueClients,
            ISNULL(SUM(r.AmountAC), 0)                AS TotalRevenue,
            ISNULL(AVG(r.AmountAC), 0)                AS AvgCheck,
            ISNULL(SUM(r.Duration), 0) / 3600.0       AS TotalHours,
            CASE WHEN ISNULL(SUM(r.Duration), 0) > 0
                THEN ISNULL(SUM(r.AmountAC), 0) / (SUM(r.Duration) / 3600.0)
                ELSE 0
            END                                       AS RevenuePerHour,
            @ObjectId, @From, @To
        FROM dbo.tbRecords r
        JOIN dbo.tbMasters m ON r.MasterId = m.Id AND r.CRMId = m.CRMId
        -- Фильтр primary / repeat через LEFT JOIN на первый визит клиента
        LEFT JOIN (
            SELECT ClientId, CRMId, MIN(DateOfAppointment) AS FirstVisit
            FROM dbo.tbRecords
            WHERE Status = 1 AND YClientsId = @ObjectId
            GROUP BY ClientId, CRMId
        ) fv ON r.ClientId = fv.ClientId AND r.CRMId = fv.CRMId
        WHERE r.Status = 1
            AND r.YClientsId = @ObjectId
            AND r.DateOfAppointment >= @From
            AND r.DateOfAppointment < DATEADD(DAY, 1, @To)
            AND (
                @Filter = 'all'
                OR (@Filter = 'primary' AND r.DateOfAppointment = fv.FirstVisit)
                OR (@Filter = 'repeat'  AND r.DateOfAppointment > fv.FirstVisit)
            )
        GROUP BY r.MasterId, m.Name, r.CRMId
        ORDER BY TotalRevenue DESC
        OFFSET 0 ROWS;
        RETURN;
    END;

    -- ── service ─────────────────────────────────────────────────────
    IF @GroupBy = 'service'
    BEGIN
        INSERT INTO @Result
            (GroupKey, GroupId, Visits, UniqueClients, TotalRevenue, AvgCheck,
             ObjectId, DateFrom, DateTo)
        SELECT
            ISNULL(ss.Name, CAST(r.ServiceId AS NVARCHAR(20))) AS GroupKey,
            r.ServiceId                               AS GroupId,
            COUNT(*)                                  AS Visits,
            COUNT(DISTINCT r.ClientId)                AS UniqueClients,
            ISNULL(SUM(r.AmountAC), 0)                AS TotalRevenue,
            ISNULL(AVG(r.AmountAC), 0)                AS AvgCheck,
            @ObjectId, @From, @To
        FROM dbo.tbRecords r
        LEFT JOIN dbo.tbServicesSettings ss ON r.ServiceId = ss.ServiceId AND r.CRMId = ss.CRMId
        LEFT JOIN (
            SELECT ClientId, CRMId, MIN(DateOfAppointment) AS FirstVisit
            FROM dbo.tbRecords
            WHERE Status = 1 AND YClientsId = @ObjectId
            GROUP BY ClientId, CRMId
        ) fv ON r.ClientId = fv.ClientId AND r.CRMId = fv.CRMId
        WHERE r.Status = 1
            AND r.YClientsId = @ObjectId
            AND r.DateOfAppointment >= @From
            AND r.DateOfAppointment < DATEADD(DAY, 1, @To)
            AND (
                @Filter = 'all'
                OR (@Filter = 'primary' AND r.DateOfAppointment = fv.FirstVisit)
                OR (@Filter = 'repeat'  AND r.DateOfAppointment > fv.FirstVisit)
            )
        GROUP BY r.ServiceId, ss.Name, r.CRMId
        ORDER BY TotalRevenue DESC
        OFFSET 0 ROWS;
        RETURN;
    END;

    -- ── salon ───────────────────────────────────────────────────────
    IF @GroupBy = 'salon'
    BEGIN
        INSERT INTO @Result
            (GroupKey, GroupId, Visits, UniqueClients, TotalRevenue, AvgCheck,
             ActiveMasters, ObjectId, DateFrom, DateTo)
        SELECT
            di.Name                                   AS GroupKey,
            r.YClientsId                              AS GroupId,
            COUNT(*)                                  AS Visits,
            COUNT(DISTINCT r.ClientId)                AS UniqueClients,
            ISNULL(SUM(r.AmountAC), 0)                AS TotalRevenue,
            ISNULL(AVG(r.AmountAC), 0)                AS AvgCheck,
            COUNT(DISTINCT r.MasterId)                AS ActiveMasters,
            @ObjectId, @From, @To
        FROM dbo.tbRecords r
        JOIN dbo.tbDatasetItems di ON r.YClientsId = di.SalonId
        LEFT JOIN (
            SELECT ClientId, CRMId, MIN(DateOfAppointment) AS FirstVisit
            FROM dbo.tbRecords
            WHERE Status = 1
              AND (@ObjectId IS NULL OR YClientsId = @ObjectId)
            GROUP BY ClientId, CRMId
        ) fv ON r.ClientId = fv.ClientId AND r.CRMId = fv.CRMId
        WHERE r.Status = 1
            AND (@ObjectId IS NULL OR r.YClientsId = @ObjectId)
            AND r.DateOfAppointment >= @From
            AND r.DateOfAppointment < DATEADD(DAY, 1, @To)
            AND (
                @Filter = 'all'
                OR (@Filter = 'primary' AND r.DateOfAppointment = fv.FirstVisit)
                OR (@Filter = 'repeat'  AND r.DateOfAppointment > fv.FirstVisit)
            )
        GROUP BY r.YClientsId, di.Name
        ORDER BY TotalRevenue DESC
        OFFSET 0 ROWS;
        RETURN;
    END;

    -- ── channel ─────────────────────────────────────────────────────
    -- Агрегация по tbRecords.Channel (канал источника записи)
    IF @GroupBy = 'channel'
    BEGIN
        INSERT INTO @Result
            (GroupKey, Visits, UniqueClients, TotalRevenue, AvgCheck,
             ObjectId, DateFrom, DateTo)
        SELECT
            ISNULL(r.Channel, N'Не указан')          AS GroupKey,
            COUNT(*)                                  AS Visits,
            COUNT(DISTINCT r.ClientId)                AS UniqueClients,
            ISNULL(SUM(r.AmountAC), 0)                AS TotalRevenue,
            ISNULL(AVG(r.AmountAC), 0)                AS AvgCheck,
            @ObjectId, @From, @To
        FROM dbo.tbRecords r
        LEFT JOIN (
            SELECT ClientId, CRMId, MIN(DateOfAppointment) AS FirstVisit
            FROM dbo.tbRecords
            WHERE Status = 1 AND YClientsId = @ObjectId
            GROUP BY ClientId, CRMId
        ) fv ON r.ClientId = fv.ClientId AND r.CRMId = fv.CRMId
        WHERE r.Status = 1
            AND r.YClientsId = @ObjectId
            AND r.DateOfAppointment >= @From
            AND r.DateOfAppointment < DATEADD(DAY, 1, @To)
            AND (
                @Filter = 'all'
                OR (@Filter = 'primary' AND r.DateOfAppointment = fv.FirstVisit)
                OR (@Filter = 'repeat'  AND r.DateOfAppointment > fv.FirstVisit)
            )
        GROUP BY r.Channel
        ORDER BY Visits DESC
        OFFSET 0 ROWS;
        RETURN;
    END;

    -- ── week ────────────────────────────────────────────────────────
    IF @GroupBy = 'week'
    BEGIN
        INSERT INTO @Result
            (GroupKey, Visits, UniqueClients, TotalRevenue, AvgCheck,
             ActiveMasters, ObjectId, DateFrom, DateTo)
        SELECT
            CAST(r.EndOfWeek AS NVARCHAR(20))         AS GroupKey,
            COUNT(*)                                  AS Visits,
            COUNT(DISTINCT r.ClientId)                AS UniqueClients,
            ISNULL(SUM(r.AmountAC), 0)                AS TotalRevenue,
            ISNULL(AVG(r.AmountAC), 0)                AS AvgCheck,
            COUNT(DISTINCT r.MasterId)                AS ActiveMasters,
            @ObjectId, @From, @To
        FROM dbo.tbRecords r
        LEFT JOIN (
            SELECT ClientId, CRMId, MIN(DateOfAppointment) AS FirstVisit
            FROM dbo.tbRecords
            WHERE Status = 1 AND YClientsId = @ObjectId
            GROUP BY ClientId, CRMId
        ) fv ON r.ClientId = fv.ClientId AND r.CRMId = fv.CRMId
        WHERE r.Status = 1
            AND r.YClientsId = @ObjectId
            AND r.DateOfAppointment >= @From
            AND r.DateOfAppointment < DATEADD(DAY, 1, @To)
            AND (
                @Filter = 'all'
                OR (@Filter = 'primary' AND r.DateOfAppointment = fv.FirstVisit)
                OR (@Filter = 'repeat'  AND r.DateOfAppointment > fv.FirstVisit)
            )
        GROUP BY r.EndOfWeek
        ORDER BY r.EndOfWeek
        OFFSET 0 ROWS;
        RETURN;
    END;

    -- ── month ───────────────────────────────────────────────────────
    IF @GroupBy = 'month'
    BEGIN
        INSERT INTO @Result
            (GroupKey, Visits, UniqueClients, TotalRevenue, AvgCheck,
             ActiveMasters, ObjectId, DateFrom, DateTo)
        SELECT
            CAST(r.EndOfMonth AS NVARCHAR(20))        AS GroupKey,
            COUNT(*)                                  AS Visits,
            COUNT(DISTINCT r.ClientId)                AS UniqueClients,
            ISNULL(SUM(r.AmountAC), 0)                AS TotalRevenue,
            ISNULL(AVG(r.AmountAC), 0)                AS AvgCheck,
            COUNT(DISTINCT r.MasterId)                AS ActiveMasters,
            @ObjectId, @From, @To
        FROM dbo.tbRecords r
        LEFT JOIN (
            SELECT ClientId, CRMId, MIN(DateOfAppointment) AS FirstVisit
            FROM dbo.tbRecords
            WHERE Status = 1 AND YClientsId = @ObjectId
            GROUP BY ClientId, CRMId
        ) fv ON r.ClientId = fv.ClientId AND r.CRMId = fv.CRMId
        WHERE r.Status = 1
            AND r.YClientsId = @ObjectId
            AND r.DateOfAppointment >= @From
            AND r.DateOfAppointment < DATEADD(DAY, 1, @To)
            AND (
                @Filter = 'all'
                OR (@Filter = 'primary' AND r.DateOfAppointment = fv.FirstVisit)
                OR (@Filter = 'repeat'  AND r.DateOfAppointment > fv.FirstVisit)
            )
        GROUP BY r.EndOfMonth
        ORDER BY r.EndOfMonth
        OFFSET 0 ROWS;
        RETURN;
    END;

    -- ── total (fallback и явный) ─────────────────────────────────────
    INSERT INTO @Result
        (GroupKey, Visits, UniqueClients, TotalRevenue, AvgCheck,
         ActiveMasters, TotalHours, ObjectId, DateFrom, DateTo)
    SELECT
        N'total'                                      AS GroupKey,
        COUNT(*)                                      AS Visits,
        COUNT(DISTINCT r.ClientId)                    AS UniqueClients,
        ISNULL(SUM(r.AmountAC), 0)                    AS TotalRevenue,
        ISNULL(AVG(r.AmountAC), 0)                    AS AvgCheck,
        COUNT(DISTINCT r.MasterId)                    AS ActiveMasters,
        ISNULL(SUM(r.Duration), 0) / 3600.0           AS TotalHours,
        @ObjectId, @From, @To
    FROM dbo.tbRecords r
    LEFT JOIN (
        SELECT ClientId, CRMId, MIN(DateOfAppointment) AS FirstVisit
        FROM dbo.tbRecords
        WHERE Status = 1 AND YClientsId = @ObjectId
        GROUP BY ClientId, CRMId
    ) fv ON r.ClientId = fv.ClientId AND r.CRMId = fv.CRMId
    WHERE r.Status = 1
        AND r.YClientsId = @ObjectId
        AND r.DateOfAppointment >= @From
        AND r.DateOfAppointment < DATEADD(DAY, 1, @To)
        AND (
            @Filter = 'all'
            OR (@Filter = 'primary' AND r.DateOfAppointment = fv.FirstVisit)
            OR (@Filter = 'repeat'  AND r.DateOfAppointment > fv.FirstVisit)
        );

    RETURN;
END;
GO
