from station_station_data import *
import argparse


def main():
    parser = argparse.ArgumentParser(description="Lire un fichier passé en argument de la ligne de commande")
    parser.add_argument("file_path", help="Path to the file to read")

    args = parser.parse_args()

    try:
        with open(args.file_path, "r", encoding="utf-8") as f:
            content = f.read()
            print("File content:\n")
            print(content)
    except FileNotFoundError:
        print(f"Error: File not found -> {args.file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
