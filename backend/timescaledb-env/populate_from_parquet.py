#!/usr/bin/env python
"""
Script pour peupler la base de données TimescaleDB avec les données du fichier Parquet.
Ce script utilise les modèles Django pour insérer les données sans modifier le schéma.
"""

import os
import sys
from datetime import UTC, datetime

import django
import pandas as pd

from weather.models import HoraireTempsReel, Quotidienne, Station

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


def parse_datetime(date_str):
    """Convertir une chaîne de date AAAAMMJJHH en datetime."""
    try:
        if isinstance(date_str, pd.Timestamp):
            return date_str.to_pydatetime()
        elif isinstance(date_str, str):
            return datetime.strptime(str(date_str), "%Y%m%d%H")
        else:
            return None
    except (ValueError, TypeError):
        return None


def get_or_create_station(code, nom, lat, lon, alt):
    """Créer ou récupérer une station."""
    station, created = Station.objects.get_or_create(
        code=code,
        defaults={
            "nom": nom,
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "departement": int(code[:2]),  # Extraire le département du code
            "poste_ouvert": True,
            "poste_public": True,
        },
    )
    return station


def populate_stations(df):
    """Peupler les stations à partir du DataFrame."""
    print("Peuplement des stations...")

    stations_info = df[
        ["NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI"]
    ].drop_duplicates()

    for _, row in stations_info.iterrows():
        station = get_or_create_station(
            code=str(row["NUM_POSTE"]),
            nom=str(row["NOM_USUEL"]),
            lat=float(row["LAT"]),
            lon=float(row["LON"]),
            alt=float(row["ALTI"]),
        )
        print(f"  Station {station.code} - {station.nom}")

    print(f"  {stations_info.shape[0]} stations traitées.")


def populate_horaire_data(df):
    """Peupler les données horaires."""
    print("Peuplement des données horaires...")

    count = 0
    for _, row in df.iterrows():
        station = Station.objects.get(code=str(row["NUM_POSTE"]))

        dt = parse_datetime(row["AAAAMMJJHH"])
        horaire = HoraireTempsReel(
            station=station,
            lat=float(row["LAT"]),
            lon=float(row["LON"]),
            reference_time=dt.replace(tzinfo=UTC) if dt else None,
            insert_time=datetime.now(UTC),
            validity_time=dt.replace(tzinfo=UTC) if dt else None,
            t=float(row["T"]) if pd.notna(row["T"]) else None,
            td=float(row["TD"]) if pd.notna(row["TD"]) else None,
            tx=float(row["TX"]) if pd.notna(row["TX"]) else None,
            tn=float(row["TN"]) if pd.notna(row["TN"]) else None,
            u=int(row["U"]) if pd.notna(row["U"]) else None,
            ux=int(row["UX"]) if pd.notna(row["UX"]) else None,
            un=int(row["UN"]) if pd.notna(row["UN"]) else None,
            dd=int(row["DD"]) if pd.notna(row["DD"]) else None,
            ff=float(row["FF"]) if pd.notna(row["FF"]) else None,
            dxy=int(row["DXY"]) if pd.notna(row["DXY"]) else None,
            fxy=float(row["FXY"]) if pd.notna(row["FXY"]) else None,
            dxi=int(row["DXI"]) if pd.notna(row["DXI"]) else None,
            fxi=float(row["FXI"]) if pd.notna(row["FXI"]) else None,
            rr1=float(row["RR1"]) if pd.notna(row["RR1"]) else None,
            t_10=float(row["T10"]) if pd.notna(row["T10"]) else None,
            t_20=float(row["T20"]) if pd.notna(row["T20"]) else None,
            t_50=float(row["T50"]) if pd.notna(row["T50"]) else None,
            t_100=float(row["T100"]) if pd.notna(row["T100"]) else None,
            vv=int(row["VV"]) if pd.notna(row["VV"]) else None,
            n=int(row["N"]) if pd.notna(row["N"]) else None,
            pres=float(row["PSTAT"]) if pd.notna(row["PSTAT"]) else None,
            pmer=float(row["PMER"]) if pd.notna(row["PMER"]) else None,
        )
        horaire.save()
        count += 1

        if count % 1000 == 0:
            print(f"  {count} enregistrements horaires traités...")

    print(f"  {count} enregistrements horaires insérés.")


def populate_quotidienne_data(df):
    """Peupler les données quotidiennes."""
    print("Peuplement des données quotidiennes...")

    df["DATE"] = df["AAAAMMJJHH"].dt.strftime("%Y%m%d")
    grouped = df.groupby(["NUM_POSTE", "DATE"])

    count = 0
    for (num_poste, date_str), group in grouped:
        station = Station.objects.get(code=str(num_poste))

        quotidienne = Quotidienne(
            station=station,
            nom_usuel=str(group["NOM_USUEL"].iloc[0]),
            lat=float(group["LAT"].iloc[0]),
            lon=float(group["LON"].iloc[0]),
            alti=float(group["ALTI"].iloc[0]),
            date=datetime.strptime(date_str, "%Y%m%d").date(),
            rr=float(group["RR1"].sum()) if pd.notna(group["RR1"].sum()) else None,
            qrr=1 if pd.notna(group["RR1"].sum()) else None,
            tn=float(group["TN"].min()) if pd.notna(group["TN"].min()) else None,
            qtn=1 if pd.notna(group["TN"].min()) else None,
            htn=str(int(group["HTN"].iloc[0]))
            if pd.notna(group["HTN"].iloc[0])
            else None,
            qhtn=1 if pd.notna(group["HTN"].iloc[0]) else None,
            tx=float(group["TX"].max()) if pd.notna(group["TX"].max()) else None,
            qtx=1 if pd.notna(group["TX"].max()) else None,
            htx=str(int(group["HTX"].iloc[0]))
            if pd.notna(group["HTX"].iloc[0])
            else None,
            qhtx=1 if pd.notna(group["HTX"].iloc[0]) else None,
            tm=float(group["T"].mean()) if pd.notna(group["T"].mean()) else None,
            qtm=1 if pd.notna(group["T"].mean()) else None,
            tampli=float(group["TX"].max() - group["TN"].min())
            if pd.notna(group["TX"].max()) and pd.notna(group["TN"].min())
            else None,
            qtampli=1
            if pd.notna(group["TX"].max()) and pd.notna(group["TN"].min())
            else None,
            ffm=float(group["FF"].mean()) if pd.notna(group["FF"].mean()) else None,
            qffm=1 if pd.notna(group["FF"].mean()) else None,
            fxy=float(group["FXY"].max()) if pd.notna(group["FXY"].max()) else None,
            qfxy=1 if pd.notna(group["FXY"].max()) else None,
            dxy=int(group["DXY"].iloc[0]) if pd.notna(group["DXY"].iloc[0]) else None,
            qdxy=1 if pd.notna(group["DXY"].iloc[0]) else None,
            hxy=str(int(group["HXY"].iloc[0]))
            if pd.notna(group["HXY"].iloc[0])
            else None,
            qhxy=1 if pd.notna(group["HXY"].iloc[0]) else None,
        )
        quotidienne.save()
        count += 1

        if count % 100 == 0:
            print(f"  {count} enregistrements quotidiens traités...")

    print(f"  {count} enregistrements quotidiens insérés.")


def main():
    print("Début du peuplement de la base de données...")

    print("Lecture du fichier Parquet...")
    parquet_path = os.path.join(os.path.dirname(__file__), "real_data_2025.parquet")
    df = pd.read_parquet(parquet_path)
    print(f"  {len(df)} enregistrements lus.")

    populate_stations(df)
    populate_horaire_data(df)
    populate_quotidienne_data(df)

    print("Peuplement terminé avec succès !")


if __name__ == "__main__":
    main()
