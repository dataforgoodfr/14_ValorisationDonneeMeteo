DROP TABLE IF EXISTS public.baseline_station_daily_mean_1991_2020;

CREATE TABLE public.baseline_station_daily_mean_1991_2020 (
    station_code TEXT NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    sample_count INTEGER NOT NULL,
    baseline_mean_tntxm NUMERIC(6,2) NOT NULL,
    PRIMARY KEY (station_code, month, day)
);

CREATE INDEX idx_baseline_station_daily_mean
ON public.baseline_station_daily_mean_1991_2020 (station_code, month, day);
