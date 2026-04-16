-- Adminer 5.4.1 PostgreSQL 17.5 dump

DROP TABLE IF EXISTS "Quotidienne";
CREATE TABLE "public"."Quotidienne" (
    "NUM_POSTE" character(8) NOT NULL,
    "NOM_USUEL" character varying(255) NOT NULL,
    "LAT" double precision NOT NULL,
    "LON" double precision NOT NULL,
    "ALTI" double precision NOT NULL,
    "AAAAMMJJ" timestamp(3) NOT NULL,
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


DROP TABLE IF EXISTS "Station";
CREATE TABLE "public"."Station" (
    "createdAt" timestamp(3) DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updatedAt" timestamp(3) NOT NULL,
    "id" character(8) NOT NULL,
    "nom" text NOT NULL,
    "departement" integer NOT NULL,
    "frequence" character varying(15) NOT NULL,
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

/*
La table station_classe contient les évolutions des classes des stations
au cours de leur vie.
*/
DROP TABLE IF EXISTS "station_classe";
CREATE TABLE "public"."station_classe" (
    "station_code" character(8) NOT NULL,
    "classe" integer NOT NULL,
    "date_debut" timestamp(3) NOT NULL,
    "date_fin" timestamp(3),
    CONSTRAINT "Station_classe_pkey" PRIMARY KEY ("station_code", "date_debut")
)
WITH (oids = false);

CREATE INDEX "Station_date_debut_idx" ON public."station_classe" USING btree (date_debut);

CREATE INDEX "Station_date_fin_idx" ON public."station_classe" USING btree (date_fin);


/*
La table station_date_creation contient la date de création et la date de
fermeture des stations.
*/
DROP TABLE IF EXISTS "station_creation_date";
CREATE TABLE "public"."station_creation_date" (
    "station_code" character(8) NOT NULL,
    "annee_de_creation" integer NOT NULL,
    "annee_de_fermeture" integer,
    CONSTRAINT "Station_creation_date_pkey" PRIMARY KEY ("station_code")
)
WITH (oids = false);

CREATE INDEX "Station_annee_de_creation_idx" ON public."station_creation_date" USING btree (annee_de_creation);

CREATE INDEX "Station_annee_de_fermeture_idx" ON public."station_creation_date" USING btree (annee_de_fermeture);
