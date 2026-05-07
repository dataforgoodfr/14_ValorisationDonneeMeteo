DROP TABLE IF EXISTS public.mv_itn_absolute_extremes_daily;
CREATE TABLE public.mv_itn_absolute_extremes_daily (
    month        integer          NOT NULL,
    day_of_month integer          NOT NULL,
    absolute_min double precision NOT NULL,
    absolute_max double precision NOT NULL,
    CONSTRAINT pk_mv_itn_absolute_extremes_daily PRIMARY KEY (month, day_of_month)
);

DROP TABLE IF EXISTS public.mv_itn_absolute_extremes_monthly;
CREATE TABLE public.mv_itn_absolute_extremes_monthly (
    month        integer          NOT NULL,
    absolute_min double precision NOT NULL,
    absolute_max double precision NOT NULL,
    CONSTRAINT pk_mv_itn_absolute_extremes_monthly PRIMARY KEY (month)
);

DROP TABLE IF EXISTS public.mv_itn_absolute_extremes_yearly;
CREATE TABLE public.mv_itn_absolute_extremes_yearly (
    absolute_min double precision NOT NULL,
    absolute_max double precision NOT NULL
);
