-- Vue : ITN journalier toutes années, avec 29 fév synthétique.
-- Équivalent de 620_002_v_itn_daily_1991_2020_with_feb29.sql pour toutes les années.
-- Pour les années non bissextiles, le 29 fév est interpolé = (itn_28fév + itn_1mar) / 2.
CREATE OR REPLACE VIEW public.v_itn_daily_all_years_with_feb29 AS
WITH feb29_fictive AS (
    SELECT
        NULL::date AS date,
        feb28.year AS year,
        2          AS month,
        29         AS day_of_month,
        TRUE       AS is_fictive,
        (feb28.itn + mar01.itn) / 2.0 AS itn
    FROM public.mv_itn_daily_all_years feb28
        INNER JOIN public.mv_itn_daily_all_years mar01
            ON  mar01.year         = feb28.year
                AND mar01.month        = 3
                AND mar01.day_of_month = 1
    WHERE feb28.month        = 2
      AND feb28.day_of_month = 28
      AND NOT (
          (feb28.year % 4 = 0 AND feb28.year % 100 <> 0)
          OR (feb28.year % 400 = 0)
      )
)
SELECT *
FROM (
    SELECT * FROM public.mv_itn_daily_all_years
    UNION ALL
    SELECT * FROM feb29_fictive
) x;
