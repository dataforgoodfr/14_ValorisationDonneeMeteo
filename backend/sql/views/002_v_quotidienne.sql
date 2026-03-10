CREATE OR REPLACE VIEW public.v_quotidienne_itn AS
SELECT
  q."NUM_POSTE"::text AS station_code,
  q."AAAAMMJJ"::date  AS date,
  q."TNTXM"           AS tntxm
FROM public."Quotidienne" q
WHERE q."TNTXM" IS NOT NULL;
