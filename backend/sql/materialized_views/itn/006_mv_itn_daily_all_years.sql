-- Vue matérialisée : ITN journalier sur toutes les années disponibles.
-- Équivalent de 001_mv_itn_daily_1991_2020_real.sql sans la restriction de période.
-- Accepte les jours avec au moins 29 stations sur 30 (HAVING COUNT >= 29).
DROP MATERIALIZED VIEW IF EXISTS mv_itn_daily_all_years;

CREATE MATERIALIZED VIEW mv_itn_daily_all_years AS
WITH source AS (
    SELECT
        q.station_code AS station_code,
        q.date         AS day,
        q.tntxm        AS tntxm
    FROM v_quotidienne_itn q
    WHERE q.station_code IN (
        '47091001','20148001','25056001','33281001','73054001',
        '29075001','14137001','36063001','63113001','16089001',
        '21473001','72181001','59343001','69029001','13054001',
        '26198001','54526001','44020001','58160001','06088001',
        '30189001','45055001','75114001','64549001','66136001',
        '86027001','35281001','67124001','31069001',
        '51183001','51449002'
    )
),
normalized AS (
    SELECT *
    FROM source
    WHERE NOT (
        station_code = CASE
            WHEN day < DATE '2012-05-08' THEN '51449002'
            ELSE '51183001'
        END
    )
)
SELECT
    n.day                          AS date,
    EXTRACT(YEAR  FROM n.day)::int AS year,
    EXTRACT(MONTH FROM n.day)::int AS month,
    EXTRACT(DAY   FROM n.day)::int AS day_of_month,
    FALSE                          AS is_fictive,
    AVG(n.tntxm)                   AS itn
FROM normalized n
GROUP BY n.day
HAVING COUNT(DISTINCT n.station_code) >= 29
ORDER BY n.day;

CREATE UNIQUE INDEX idx_mv_itn_daily_all_years_date
    ON mv_itn_daily_all_years (date);

CREATE INDEX idx_mv_itn_daily_all_years_month_day
    ON mv_itn_daily_all_years (month, day_of_month);

CREATE INDEX idx_mv_itn_daily_all_years_year
    ON mv_itn_daily_all_years (year);
