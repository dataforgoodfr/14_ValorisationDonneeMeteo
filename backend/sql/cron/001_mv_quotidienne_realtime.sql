CREATE EXTENSION IF NOT EXISTS pg_cron;

SELECT cron.schedule(
   'refresh-mv-quotidienne-realtime',
   '*/6 * * * *',
   $$
   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_quotidienne_realtime;
   REFRESH MATERIALIZED VIEW mv_itn_daily_all_years;
   REFRESH MATERIALIZED VIEW mv_itn_daily_all_years_with_feb29;
   REFRESH MATERIALIZED VIEW mv_itn_absolute_extremes_daily;
   REFRESH MATERIALIZED VIEW mv_itn_absolute_extremes_monthly;
   REFRESH MATERIALIZED VIEW mv_itn_absolute_extremes_yearly;
   $$
);
