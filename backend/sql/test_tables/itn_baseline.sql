DROP TABLE IF EXISTS public.mv_itn_baseline_1991_2020;
CREATE TABLE public.mv_itn_baseline_1991_2020 (
    month integer NOT NULL,
    day_of_month integer NOT NULL,
    sample_size integer NOT NULL,
    itn_mean double precision NOT NULL,
    itn_stddev double precision NOT NULL,
    itn_p20 double precision NOT NULL,
    itn_p80 double precision NOT NULL,
    CONSTRAINT pk_mv_itn_baseline_1991_2020 PRIMARY KEY (month, day_of_month)
);

DROP TABLE IF EXISTS public.mv_itn_baseline_monthly_1991_2020;
CREATE TABLE public.mv_itn_baseline_monthly_1991_2020 (
    month integer NOT NULL,
    sample_size integer NOT NULL,
    itn_mean double precision NOT NULL,
    itn_stddev double precision NOT NULL,
    itn_p20 double precision NOT NULL,
    itn_p80 double precision NOT NULL,
    CONSTRAINT pk_mv_itn_baseline_monthly_1991_2020 PRIMARY KEY (month)
);

DROP TABLE IF EXISTS public.mv_itn_baseline_yearly_1991_2020;
CREATE TABLE public.mv_itn_baseline_yearly_1991_2020 (
    sample_size integer NOT NULL,
    itn_mean double precision NOT NULL,
    itn_stddev double precision NOT NULL,
    itn_p20 double precision NOT NULL,
    itn_p80 double precision NOT NULL,
    CONSTRAINT pk_mv_itn_baseline_yearly_1991_2020 PRIMARY KEY (sample_size)
);
