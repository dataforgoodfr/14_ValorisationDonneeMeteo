import argparse

from stationJsonDataProcessors import *


def main():
    parser = argparse.ArgumentParser(
        description="Lire un fichier passé en argument de la ligne de commande"
    )
    parser.add_argument("file_path", help="Chemin du fichier à lire")

    args = parser.parse_args()

    try:
        with open(args.file_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found -> {args.file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    station_csv = StationDataProcessor(args.file_path)
    station_csv.extract_data()
    station_csv.prepare_table_station_classe()
    station_csv.prepare_table_station_creation_date()
    station_csv.store_data()


if __name__ == "__main__":
    main()
