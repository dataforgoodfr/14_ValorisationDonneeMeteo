import argparse
import csv
import json
import logging
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol, TypeAlias

import pdfplumber
import requests
from pdfminer.pdfexceptions import PDFException
from pdfplumber.utils.exceptions import PdfminerException
from rest_framework.response import Response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

DEFAULT_MAX_PDFS_TO_READ: int | None = None

StationCode: TypeAlias = str


@dataclass
class TemperatureClass:
    classe: str | None = None
    debut: str | None = None
    fin: str | None = None


@dataclass
class StationInfo:
    station_code: StationCode
    url: str
    departement: str | None
    creation_date: str | None
    closure_date: str | None
    classes_temperature: list[TemperatureClass]


ITN_STATIONS_IDS = (
    "06088001",
    "13054001",
    "14137001",
    "16089001",
    "20148001",
    "21473001",
    "25056001",
    "26198001",
    "29075001",
    "30189001",
    "31069001",
    "33281001",
    "35281001",
    "36063001",
    "44020001",
    "45055001",
    "47091001",
    "51183001",
    "51449002",
    "54526001",
    "58160001",
    "59343001",
    "63113001",
    "64549001",
    "66136001",
    "67124001",
    "69029001",
    "72181001",
    "73054001",
    "75114001",
    "86027001",
)


def get_pdf_urls_cache_path(script_dir: Path) -> Path:
    return script_dir / "pdf_urls.json"


def load_cached_pdf_urls(cache_file_path: Path) -> list[str]:
    with open(cache_file_path, encoding="utf-8") as file:
        return json.load(file)


def fetch_urls(api_url: str) -> list[str]:
    response = requests.get(api_url)
    data = response.json().get("resources", [])
    return [
        res["url"] for res in data if res.get("url") and res.get("url").endswith(".pdf")
    ]


def save_pdf_urls(pdf_urls: list[str], cache_file_path: Path) -> None:
    ensure_directory_exists(cache_file_path)
    with open(cache_file_path, mode="w", encoding="utf-8") as file:
        json.dump(pdf_urls, file, indent=4, ensure_ascii=False)


def get_pdf_urls(*, script_dir: Path, update: bool = False) -> list[str]:
    api_url = "https://www.data.gouv.fr/api/1/datasets/67a1e85a366f75613f750296/"
    cache_file_path = get_pdf_urls_cache_path(script_dir)

    if cache_file_path.exists() and not update:
        logger.debug("Reading cached PDF URLs from %s", cache_file_path)
        return load_cached_pdf_urls(cache_file_path)

    pdf_urls = fetch_urls(api_url)
    pdf_urls = sorted(pdf_urls)
    save_pdf_urls(pdf_urls, cache_file_path)
    return pdf_urls


def build_station_info_from_text(
    station_id: StationCode,
    pdf_url: str,
    text: str,
) -> StationInfo:
    classes = extract_classes(text)
    creation_date = extract_creation_date(text)
    closure_date = extract_closure_date(text)
    departement_info = extract_departement(text)

    return StationInfo(
        station_code=station_id,
        url=pdf_url,
        departement=departement_info["code"],
        creation_date=creation_date,
        closure_date=closure_date,
        classes_temperature=classes,
    )


def get_meteofrance_data_dict(
    *,
    update: bool = False,
    itn_only: bool = False,
    station_filter: set[StationCode] | None = None,
    max_pdfs: int | None = DEFAULT_MAX_PDFS_TO_READ,
    keep_pdf: bool = False,
    parallelism: int = 1,
) -> dict[StationCode, StationInfo]:
    data_dict: dict[StationCode, StationInfo] = {}
    script_dir = Path(__file__).parent
    pdf_urls = get_pdf_urls(script_dir=script_dir, update=update)
    selected_stations: list[tuple[StationCode, str, int]] = []
    seen_station_ids: set[StationCode] = set()

    for i, pdf_url in enumerate(pdf_urls, 1):
        station_id = extract_id(pdf_url)

        if (
            station_id is None
            or station_id in seen_station_ids
            or (itn_only and station_id not in ITN_STATIONS_IDS)
            or (station_filter is not None and station_id not in station_filter)
        ):
            continue

        seen_station_ids.add(station_id)
        selected_stations.append((station_id, pdf_url, i))

    if max_pdfs:
        selected_stations = selected_stations[:max_pdfs]

    total = len(selected_stations)

    def process_station(
        station_id: StationCode,
        pdf_url: str,
        position: int,
    ) -> tuple[StationCode, StationInfo]:
        logger.info("Processing station %s (%d/%d)", station_id, position, total)

        station_info = get_station_info(
            station_id=station_id,
            pdf_url=pdf_url,
            script_dir=script_dir,
            update=update,
            keep_pdf=keep_pdf,
        )
        return station_id, station_info

    if parallelism <= 1:
        for station_id, pdf_url, position in selected_stations:
            resolved_station_id, station_info = process_station(
                station_id=station_id,
                pdf_url=pdf_url,
                position=position,
            )
            data_dict[resolved_station_id] = station_info
        return data_dict

    with ThreadPoolExecutor(max_workers=parallelism) as executor:
        futures = [
            executor.submit(
                process_station,
                station_id,
                pdf_url,
                position,
            )
            for station_id, pdf_url, position in selected_stations
        ]

        for future in as_completed(futures):
            station_id, station_info = future.result()
            data_dict[station_id] = station_info

    return data_dict


def get_pdf(pdf_url: str) -> Response:
    return requests.get(pdf_url)


def save_pdf(filename: Path, pdf_resp: Response) -> None:
    with open(filename, "wb") as f:
        f.write(pdf_resp.content)


def download_and_save_pdf(pdf_url: str, filename: Path) -> None:
    pdf_resp = get_pdf(pdf_url)
    save_pdf(filename, pdf_resp)


def get_station_info(
    *,
    station_id: StationCode,
    pdf_url: str,
    script_dir: Path,
    update: bool,
    keep_pdf: bool,
) -> StationInfo:
    try:
        text = get_station_text(
            station_id=station_id,
            pdf_url=pdf_url,
            script_dir=script_dir,
            update=update,
            keep_pdf=keep_pdf,
        )
        return build_station_info_from_text(station_id, pdf_url, text)
    except (OSError, PDFException, PdfminerException):
        logger.warning("Failed to parse station %s, marking as failed", station_id)
        return StationInfo(
            station_code=station_id,
            url=pdf_url,
            departement=None,
            creation_date=None,
            closure_date=None,
            classes_temperature=[],
        )


def get_station_text(
    *,
    station_id: StationCode,
    pdf_url: str,
    script_dir: Path,
    update: bool,
    keep_pdf: bool,
) -> str:
    txt_filename = script_dir / "txts" / f"file_{station_id}.txt"
    pdf_filename = script_dir / "pdfs" / f"file_{station_id}.pdf"

    if txt_filename.exists() and not update:
        logger.debug("Reading text from %s", txt_filename)
        return txt_filename.read_text(encoding="utf-8")

    logger.debug("Downloading %s to %s", pdf_url, pdf_filename)
    ensure_directory_exists(pdf_filename)
    download_and_save_pdf(pdf_url, pdf_filename)

    logger.debug("Extracting text from %s", pdf_filename)
    text = extract_text_from_pdf(pdf_filename)
    logger.debug("Extracted text from %s:\n%s", pdf_filename, text)

    ensure_directory_exists(txt_filename)
    txt_filename.write_text(text, encoding="utf-8")

    if not keep_pdf:
        pdf_filename.unlink(missing_ok=True)

    return text


def extract_text_from_pdf(filename: Path) -> str:
    text = ""
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_id(pdf_url: str) -> StationCode | None:
    m = re.search(r"\d+/(\d+)", pdf_url)
    return m.group(1) if m else None


def date_dd_mm_yyyy_to_iso(date_str: str) -> str:
    """
    Convert date string in DD/MM/YYYY format to ISO 8601 format with +00:00.

    Args:
        date_str: Date string in DD/MM/YYYY format (e.g., "01/09/1920")

    Returns:
        ISO 8601 date string with +00:00 (e.g., "1920-09-01T00:00:00+00:00")
    """
    day, month, year = date_str.split("/")
    return f"{year}-{month}-{day}T00:00:00+00:00"


def extract_labeled_date(text: str, label_pattern: str) -> str | None:
    match = re.search(
        rf"{label_pattern}\s*:\s*(\d{{2}}/\d{{2}}/\d{{4}})",
        text,
        re.IGNORECASE,
    )
    return date_dd_mm_yyyy_to_iso(match.group(1)) if match else None


def extract_creation_date(text: str) -> str | None:
    return extract_labeled_date(text, r"Date d['’]ouverture")


def extract_closure_date(text: str) -> str | None:
    return extract_labeled_date(text, r"Date de fermeture")


def extract_departement(text: str) -> dict:
    """
    Extrait le nom du département et le code entre parenthèses.
    Retourne un dict : {"nom": ..., "code": ...}
    """
    pattern = r"Département\s*:\s*([^\(]+)\(?([0-9]{1,3}|2A|2B)?\)?"

    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return {"nom": None, "code": None}

    nom = match.group(1).strip()  # texte avant la parenthèse
    code = match.group(2) if match.group(2) else None  # texte entre parenthèses
    return {"nom": nom, "code": code}


def extract_classes(text: str) -> list[TemperatureClass]:
    all_classes: list[TemperatureClass] = []

    section_pattern = r"QUALITE\s+DU\s+SITE(.*?)(?=\n[A-ZÉ ]{5,}|\Z)"
    sections = re.finditer(section_pattern, text, re.DOTALL)

    for section_match in sections:
        section = section_match.group(1)

        class_matches = re.findall(
            r"\bTemperature\s+(\d+)\s+\S+\s+(\d{2}/\d{2}/\d{4})(?:\s+(\d{2}/\d{2}/\d{4}))?",
            #                  ^^^          ^^^^^^^^^^         ^^^^^^^^^^
            #                classe            Début               Fin (optional)
            section,
        )

        for c, d, f in class_matches:
            debut_iso = date_dd_mm_yyyy_to_iso(d)
            fin_iso = date_dd_mm_yyyy_to_iso(f) if f else None
            all_classes.append(TemperatureClass(classe=c, debut=debut_iso, fin=fin_iso))

    return sorted(all_classes, key=lambda t: t.debut)


def build_csv_lines(
    station_id: StationCode, info: StationInfo
) -> list[list[str | None]]:
    base_row = [
        station_id,
        info.url,
        info.departement,
        info.creation_date,
        info.closure_date,
    ]
    classes = info.classes_temperature

    return [base_row + [c.classe, c.debut, c.fin] for c in classes]


def build_classes_csv_lines(
    station_id: StationCode,
    info: StationInfo,
) -> list[list[str | None]]:
    return [[station_id, c.classe, c.debut, c.fin] for c in info.classes_temperature]


def prepare_csv_rows(
    data_dict: dict[StationCode, StationInfo],
) -> list[list[str | None]]:
    header = [
        "id",
        "url",
        "departement",
        "creation_date",
        "closure_date",
        "classe",
        "debut",
        "fin",
    ]
    rows: list[list[str | None]] = [header]
    for station_id, info in data_dict.items():
        rows.extend(build_csv_lines(station_id, info))
    return rows


def prepare_classes_csv_rows(
    data_dict: dict[StationCode, StationInfo],
) -> list[list[str | None]]:
    rows: list[list[str | None]] = [["id", "classe", "debut", "fin"]]
    for station_id, info in data_dict.items():
        rows.extend(build_classes_csv_lines(station_id, info))
    return rows


def prepare_lifecycle_csv_rows(
    data_dict: dict[StationCode, StationInfo],
) -> list[list[str | None]]:
    return [["id", "creation_date", "closure_date"]] + [
        [station_id, info.creation_date, info.closure_date]
        for station_id, info in data_dict.items()
    ]


def ensure_directory_exists(file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)


def save_csv(rows: list[list[str | None]], csv_file_path: Path) -> None:
    ensure_directory_exists(csv_file_path)
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for row in rows:
            writer.writerow(row)


def serialize_data_dict(data_dict: dict[StationCode, StationInfo]) -> dict:
    return {
        station_id: {
            "station_code": info.station_code,
            "url": info.url,
            "departement": info.departement,
            "creation_date": info.creation_date,
            "closure_date": info.closure_date,
            "classes_temperature": [asdict(tc) for tc in info.classes_temperature],
        }
        for station_id, info in data_dict.items()
    }


def save_json(data: dict, json_file_path: Path) -> None:
    ensure_directory_exists(json_file_path)
    with open(json_file_path, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


class OutputWriter(Protocol):
    """Destination-agnostic sink for the generated JSON and CSV outputs."""

    def write_json(self, filename: str, data: dict) -> None: ...

    def write_csv(self, filename: str, rows: list[list[str | None]]) -> None: ...


class FileOutputWriter:
    """Writes each output to a file inside ``output_dir``."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, filename: str, data: dict) -> None:
        save_json(data, self.output_dir / filename)

    def write_csv(self, filename: str, rows: list[list[str | None]]) -> None:
        save_csv(rows, self.output_dir / filename)


class StdoutOutputWriter:
    """Prints each output to stdout instead of writing files (dry run)."""

    def write_json(self, filename: str, data: dict) -> None:
        self._print_header(filename)
        json.dump(data, sys.stdout, indent=4, ensure_ascii=False)
        print()

    def write_csv(self, filename: str, rows: list[list[str | None]]) -> None:
        self._print_header(filename)
        writer = csv.writer(sys.stdout, lineterminator="\n")
        writer.writerows(rows)

    @staticmethod
    def _print_header(filename: str) -> None:
        print(f"\n===== {filename} =====")


def write_outputs(
    data_dict: dict[StationCode, StationInfo],
    writer: OutputWriter,
) -> None:
    writer.write_json("stations_data.json", serialize_data_dict(data_dict))
    writer.write_csv("stations_data.csv", prepare_csv_rows(data_dict))
    writer.write_csv("stations_classes.csv", prepare_classes_csv_rows(data_dict))
    writer.write_csv("stations_lifecycle.csv", prepare_lifecycle_csv_rows(data_dict))


def parse_station_ids(value: str) -> set[StationCode]:
    ids = {part.strip() for part in value.split(",") if part.strip()}
    if not ids:
        raise argparse.ArgumentTypeError("no station IDs provided")
    return ids


def parse_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download and parse Météo-France station PDF files.",
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable DEBUG log level (default: INFO).",
    )
    verbosity.add_argument(
        "-v",
        action="count",
        dest="verbosity",
        default=0,
        help="Increase verbosity; use -vvv or more to enable DEBUG (default: INFO).",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        default=False,
        help="Refresh cached PDF URLs and re-download/re-extract station files even if text already exists locally (default: False).",
    )
    parser.add_argument(
        "--save-pdf",
        action="store_true",
        default=False,
        help="Keep downloaded PDF files after text extraction (default: False).",
    )
    parser.add_argument(
        "--itn",
        action="store_true",
        default=False,
        help="Restrict processing to ITN stations only (default: all stations).",
    )
    parser.add_argument(
        "--station",
        type=parse_station_ids,
        default=None,
        dest="station_filter",
        metavar="ID[,ID...]",
        help="Process only these comma-separated station IDs (e.g. 13054001,06088001).",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        dest="max_pdfs",
        help="Maximum number of PDFs to read (default: no limit).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        dest="output_dir",
        help="Output directory (relative to cwd). Default: output/ next to this script.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print outputs to stdout instead of writing files (default: False).",
    )
    parser.add_argument(
        "--parallelism",
        type=int,
        default=1,
        help="Number of stations to process in parallel (default: 1).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_cli_args()
    if args.debug or (args.verbosity is not None and args.verbosity >= 3):
        logger.setLevel(logging.DEBUG)

    if args.parallelism < 1:
        raise ValueError("--parallelism must be >= 1")

    output_dir = (
        Path.cwd() / args.output_dir
        if args.output_dir
        else Path(__file__).parent / "output"
    )

    logger.info("Started...")
    data_dict = get_meteofrance_data_dict(
        update=args.update,
        itn_only=args.itn,
        station_filter=args.station_filter,
        max_pdfs=args.max_pdfs,
        keep_pdf=args.save_pdf,
        parallelism=args.parallelism,
    )

    writer: OutputWriter = (
        StdoutOutputWriter() if args.dry_run else FileOutputWriter(output_dir)
    )
    write_outputs(data_dict, writer)

    if args.dry_run:
        logger.info("Dry run complete; no files written.")
    else:
        logger.info("Data saved to %s", output_dir)


if __name__ == "__main__":
    main()
