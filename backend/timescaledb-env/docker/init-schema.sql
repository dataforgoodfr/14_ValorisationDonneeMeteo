-- TimeScaleDB Environment for InfoClimat Volunteers
-- Minimal schema with Station, HoraireTempsReel, and Quotidienne tables

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ============================================================================
-- Station Table
-- Metadata for weather stations
-- ============================================================================
DROP TABLE IF EXISTS "Station" CASCADE;
CREATE TABLE "public"."Station" (
    "createdAt" timestamptz(3) DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamptz(3) NOT NULL,
    "id" character(8) NOT NULL,
    "nom" text NOT NULL,
    "departement" integer NOT NULL,
    "frequence" text NOT NULL,
    "posteOuvert" boolean NOT NULL,
    "typePoste" integer NOT NULL,
    "lon" double precision NOT NULL,
    "lat" double precision NOT NULL,
    "alt" double precision NOT NULL,
    "postePublic" boolean NOT NULL,
    CONSTRAINT "Station_pkey" PRIMARY KEY ("id", "frequence")
)
WITH (oids = false);

CREATE INDEX "Station_lon_idx" ON public."Station" USING btree (lon);
CREATE INDEX "Station_lat_idx" ON public."Station" USING btree (lat);

-- ============================================================================
-- HoraireTempsReel Table
-- Real-time hourly weather measurements
-- ============================================================================
DROP TABLE IF EXISTS "HoraireTempsReel" CASCADE;
CREATE TABLE "public"."HoraireTempsReel" (
    "geo_id_insee" character(8) NOT NULL,
    "lat" double precision NOT NULL,
    "lon" double precision NOT NULL,
    "reference_time" timestamptz(3) NOT NULL,
    "insert_time" timestamptz(3) NOT NULL,
    "validity_time" timestamptz(3) NOT NULL,
    "t" double precision,
    "td" double precision,
    "tx" double precision,
    "tn" double precision,
    "u" integer,
    "ux" integer,
    "un" integer,
    "dd" integer,
    "ff" double precision,
    "dxy" integer,
    "fxy" double precision,
    "dxi" integer,
    "fxi" double precision,
    "rr1" double precision,
    "t_10" double precision,
    "t_20" double precision,
    "t_50" double precision,
    "t_100" double precision,
    "vv" integer,
    "etat_sol" integer,
    "sss" double precision,
    "n" integer,
    "insolh" double precision,
    "ray_glo01" double precision,
    "pres" double precision,
    "pmer" double precision,
    CONSTRAINT "HoraireTempsReel_pkey" PRIMARY KEY ("geo_id_insee", "validity_time")
)
WITH (oids = false);

CREATE INDEX "HoraireTempsReel_validity_time_idx" ON public."HoraireTempsReel" USING btree (validity_time);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable(
    '"HoraireTempsReel"',
    'validity_time',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '7 days'
);

-- ============================================================================
-- Quotidienne Table
-- Daily aggregated weather data
-- ============================================================================
DROP TABLE IF EXISTS "Quotidienne" CASCADE;
CREATE TABLE "public"."Quotidienne" (
    "NUM_POSTE" character(8) NOT NULL,
    "NOM_USUEL" text NOT NULL,
    "LAT" double precision NOT NULL,
    "LON" double precision NOT NULL,
    "ALTI" double precision NOT NULL,
    "AAAAMMJJ" timestamptz(3) NOT NULL,
    "RR" double precision,
    "QRR" integer,
    "TN" double precision,
    "QTN" integer,
    "HTN" character(4),
    "QHTN" integer,
    "TX" double precision,
    "QTX" integer,
    "HTX" character(4),
    "QHTX" integer,
    "TM" double precision,
    "QTM" integer,
    "TNTXM" double precision,
    "QTNTXM" integer,
    "TAMPLI" double precision,
    "QTAMPLI" integer,
    "TNSOL" double precision,
    "QTNSOL" integer,
    "TN50" double precision,
    "QTN50" integer,
    "DG" integer,
    "QDG" integer,
    "FFM" double precision,
    "QFFM" integer,
    "FF2M" double precision,
    "QFF2M" integer,
    "FXY" double precision,
    "QFXY" integer,
    "DXY" integer,
    "QDXY" integer,
    "HXY" character(4),
    "QHXY" integer,
    "FXI" double precision,
    "QFXI" integer,
    "DXI" integer,
    "QDXI" integer,
    "HXI" character(4),
    "QHXI" integer,
    "FXI2" double precision,
    "QFXI2" integer,
    "DXI2" integer,
    "QDXI2" integer,
    "HXI2" character(4),
    "QHXI2" integer,
    "FXI3S" double precision,
    "QFXI3S" integer,
    "DXI3S" integer,
    "QDXI3S" integer,
    "HXI3S" character(4),
    "QHXI3S" integer,
    "DRR" integer,
    "QDRR" integer,
    CONSTRAINT "Quotidienne_pkey" PRIMARY KEY ("NUM_POSTE", "AAAAMMJJ")
)
WITH (oids = false);

CREATE INDEX "Quotidienne_AAAAMMJJ_idx" ON public."Quotidienne" USING btree ("AAAAMMJJ");

-- Convert to hypertable for time-series optimization
SELECT create_hypertable(
    '"Quotidienne"',
    'AAAAMMJJ',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '30 days'
);

-- Display confirmation
DO $$
BEGIN
    RAISE NOTICE 'Schema initialized successfully!';
    RAISE NOTICE 'Tables created: Station, HoraireTempsReel, Quotidienne';
    RAISE NOTICE 'Hypertables configured for time-series optimization';
END $$;
