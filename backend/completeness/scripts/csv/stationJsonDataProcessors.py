import json
import os

import pandas as pd


class StationDataProcessor:
    def __init__(self, fichier_de_donnees):
        """
        Initialise l'objet StationDataProcessor.

        Args:
            fichier_de_donnees (str): Chemin vers le fichier JSON contenant les données des stations.
        """
        self.fichier_de_donnees = fichier_de_donnees

        # Initialise les listes pour stocker les données extraites
        self.station_codes = []
        self.dates_de_creation = []
        self.classes = []
        self.date_debut_de_classement = []
        self.date_fin_de_classement = []

        # définition des dataframes par défaut utilisés dans le cadre du traitement des données
        self.df_raw_station_classe = None
        self.df_processed_station_classe = None
        self.df_raw_station_creation_date = None
        self.df_processed_station_creation_date = None

    # Méthode utilitaire pour ajouter des données aux listes de l’instance
    def _ajout_de_donnees_station(
        self,
        station_code,
        date_de_creation_de_station,
        current_classe,
        date_debut,
        date_fin,
    ):
        """
        Ajoute les données d'une station à la liste interne.

        Args:
            station_code (str): Code de la station.
            date_de_creation_de_station (str): Date de création de la station.
            current_classe (str): Classe  de la station.
            date_debut (str): Date de début de la période de classement.
            date_fin (str): Date de fin de la période de classement.

        """
        self.station_codes.append(station_code)
        self.dates_de_creation.append(date_de_creation_de_station)
        self.classes.append(current_classe)
        self.date_debut_de_classement.append(date_debut)
        self.date_fin_de_classement.append(date_fin)

    def extract_data(self):
        """
        Extrait les données des stations du fichier JSON et remplit les listes internes.

        Returns:
            tuple: (dataframe_station_classe, dataframe_station_creation_date).

        """
        with open(self.fichier_de_donnees) as f:
            station_info_donnees = json.load(f)

        for station_code_key, station_details in station_info_donnees.items():
            periode_de_classement = station_details.get("classeTemperature")
            date_de_creation_de_la_station = station_details.get("creationDate")

            if isinstance(periode_de_classement, list):
                # Si la station présente une évolution des classes
                for classement in periode_de_classement:
                    self._ajout_de_donnees_station(
                        station_code_key,
                        date_de_creation_de_la_station,
                        classement.get("classe"),
                        classement.get("debut"),
                        classement.get("fin"),
                    )
            elif periode_de_classement is None:
                self._ajout_de_donnees_station(
                    station_code_key,
                    date_de_creation_de_la_station,
                    "NA",  # Utilisation de ‘NA’ comme valeur de remplacement pour les données manquantes
                    "NA",
                    "NA",
                )

        # Créer le dataframe pour la table station_classe
        self.df_raw_station_classe = pd.DataFrame(
            {
                "station_code": self.station_codes,
                "classe": self.classes,
                "date_debut": self.date_debut_de_classement,
                "date_fin": self.date_fin_de_classement,
            }
        )

        # Créer le dataframe pour la table station_creation_date
        self.df_raw_station_creation_date = pd.DataFrame(
            {
                "station_code": self.station_codes,
                "creation_date": self.dates_de_creation,
                "date_fin": self.date_fin_de_classement,
            }
        )

        return self.df_raw_station_classe, self.df_raw_station_creation_date

    def get_dataframe(self, dataframe):
        """
        Renvoie une copie du DataFrame fourni.

        Args:
            dataframe (dataframe type): dataframe fourni.

        Returns:
            dataframe: Une copie du DataFrame fourni.

        Raises:
            ValueError: Si le DataFrame fourni est None.

        """
        if dataframe is None:
            raise ValueError("Le DataFrame ne peut pas être None.")
        return dataframe.copy()

    def prepare_table_station_classe(self):
        """
        Prépare les données brut du fichier station json pour la création du fichier
        station_classe.csv.

        Returns:
            dataframe: Le dataframe traité de station_classe.

        """
        # Utilisez une copie du DataFrame brut pour le traitement
        stations = self.get_dataframe(self.df_raw_station_classe)

        # Filtre les lignes où ‘date_debut’ est égale à ‘NA’ (aucune période de classification)
        stations_avec_periode_de_classement = stations[
            stations["date_debut"] != "NA"
        ].copy()

        # Convertion de date_debut au format datetime: 1970-01-01 : 00:00:00
        stations_avec_periode_de_classement["date_debut"] = pd.to_datetime(
            stations_avec_periode_de_classement["date_debut"],
            format="%d/%m/%Y",
            errors="coerce",
            dayfirst=True,
        )

        # Convertion de date_fin au format datetime: 1970-01-01 : 00:00:00
        stations_avec_periode_de_classement["date_fin"] = pd.to_datetime(
            stations_avec_periode_de_classement["date_fin"],
            format="%d/%m/%Y",
            errors="coerce",
            dayfirst=True,
        )

        # Casting de station_code sous forme de string
        stations_avec_periode_de_classement["station_code"] = (
            stations_avec_periode_de_classement["station_code"].astype(str)
        )

        # Convertir ‘classe’ en Int64
        stations_avec_periode_de_classement["classe"] = (
            stations_avec_periode_de_classement["classe"].astype("Int64")
        )

        self.df_processed_station_classe = stations_avec_periode_de_classement
        return self.df_processed_station_classe

    def prepare_table_station_creation_date(self):
        """
        Prépare les données brut du fichier station json pour la création du fichier
        station_creation_date.csv.

        Returns:
            dataframe: Le dataframe traité de station_creation_date.

        """
        # Utilisez une copie du DataFrame brut pour le traitement
        stations_creation_date_df = self.get_dataframe(
            self.df_raw_station_creation_date
        )

        # Renomme les colonnes pour plus de clarté
        stations_creation_date_df = stations_creation_date_df.rename(
            columns={
                "creation_date": "date_de_creation_raw",
                "date_fin": "date_de_fermeture_raw",
            }
        )

        # Création de la date de creation. ex : 1970-01-01 00:00:00
        stations_creation_date_df["date_de_creation"] = (
            pd.to_datetime(
                stations_creation_date_df["date_de_creation_raw"],
                format="%m/%Y",
                errors="coerce",
            )
            .dt.to_period("M")
            .dt.to_timestamp()
        )

        # Création de l'année de fermeture
        stations_creation_date_df["annee_de_fermeture"] = pd.to_datetime(
            stations_creation_date_df["date_de_fermeture_raw"],
            format="%d/%m/%Y",
            errors="coerce",
            dayfirst=True,
        )

        # Casting de station_code sous forme de string
        stations_creation_date_df["station_code"] = stations_creation_date_df[
            "station_code"
        ].astype(str)

        # Suppression de colonnes brutes
        stations_creation_date_df = stations_creation_date_df.drop(
            columns=["date_de_creation_raw", "date_de_fermeture_raw"]
        )

        # Création de l'année de création pour la déduplication
        stations_creation_date_df["annee_de_creation"] = stations_creation_date_df[
            "date_de_creation"
        ].dt.year

        # Garder une ligne par station
        stations_creation_date_unique_stations = (
            stations_creation_date_df.drop_duplicates(
                subset=["station_code", "annee_de_creation"], keep="first"
            )
        )

        # Sélectionner les colonnes finales requises
        self.df_processed_station_creation_date = (
            stations_creation_date_unique_stations[
                ["station_code", "date_de_creation", "annee_de_fermeture"]
            ]
        )
        return self.df_processed_station_creation_date

    def store_data(self):
        """
        Stock les données préparées dans deux fichiers CSV dans le dossier backend/db_data du projet.
        Le dossier sera créé si nécessaire.

        Raises:
          ValueError: Si les données ne sont pas préparées.
        """
        if (
            self.df_processed_station_classe is None
            or self.df_processed_station_creation_date is None
        ):
            raise ValueError(
                "Les données ne sont pas préparées. Appelez d’abord « prepare_table_station_classe() » et "
                "« prepare_table_station_creation_date() »."
            )

        # Obtiens le répertoire racine
        project_root = os.getcwd()
        output_dir = os.path.join(project_root)

        # Définition des fichiers à enregistrer
        output_path_station_classe = os.path.join(output_dir, "station_classe.csv")
        output_path_station_creation_date = os.path.join(
            output_dir, "station_creation_date.csv"
        )

        # Stocke les données du csv station_classe
        self.df_processed_station_classe.to_csv(output_path_station_classe, index=False)
        print(
            f"Les données de station_classe sont stockés dans : {output_path_station_classe}"
        )

        # Stocke les données du csv station_creation_date
        self.df_processed_station_creation_date.to_csv(
            output_path_station_creation_date, index=False
        )
        print(
            f"Les données de station_creation_date sont stockés dans : {output_path_station_creation_date}"
        )
