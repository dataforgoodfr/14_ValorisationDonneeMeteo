CREATE OR REPLACE VIEW public.v_quotidienne_itn AS
SELECT
  q."NUM_POSTE" AS station_code,
  q."AAAAMMJJ"  AS date,
  q."TNTXM"     AS tntxm
FROM public."Quotidienne" q
WHERE q."TNTXM" IS NOT NULL;
