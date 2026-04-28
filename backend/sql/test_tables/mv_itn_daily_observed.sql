CREATE TABLE public.mv_itn_daily_observed (
    date date PRIMARY KEY,
    year integer NOT NULL,
    month integer NOT NULL,
    day_of_month integer NOT NULL,
    temperature double precision NOT NULL
);

INSERT INTO public.mv_itn_daily_observed
    (date, year, month, day_of_month, temperature)
VALUES
    ('2024-01-01', 2024, 1, 1, 8.0),
    ('2024-01-02', 2024, 1, 2, 10.0),
    ('2024-01-31', 2024, 1, 31, 12.0),
    ('2024-02-29', 2024, 2, 29, 14.0),
    ('2025-01-01', 2025, 1, 1, 16.0),
    ('2025-01-02', 2025, 1, 2, 18.0),
    ('2025-01-31', 2025, 1, 31, 20.0),
    ('2025-02-28', 2025, 2, 28, 22.0);
