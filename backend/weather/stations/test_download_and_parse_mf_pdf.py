import argparse

import pytest

from .download_and_parse_mf_pdf import (
    StationCode,
    StationInfo,
    TemperatureClass,
    build_classes_csv_lines,
    build_csv_lines,
    build_station_info_from_text,
    date_dd_mm_yyyy_to_iso,
    extract_classes,
    extract_closure_date,
    extract_creation_date,
    extract_departement,
    extract_id,
    parse_station_ids,
)


@pytest.mark.parametrize(
    "pdf_url, expected",
    [
        ("https://example.com/67/12345678/file.pdf", "12345678"),
        ("https://example.com/file.pdf", None),
        ("https://example.com/data/67a1e85a/98765432/report.pdf", None),
        (
            "https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/INFOS_POSTES/13/13054001_13_MARIGNANE.pdf",
            "13054001",
        ),
    ],
)
def test_extract_id(pdf_url: str, expected: StationCode | None) -> None:
    assert extract_id(pdf_url) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("13054001", {"13054001"}),
        ("13054001,06088001", {"13054001", "06088001"}),
        (" 13054001 , 06088001 ", {"13054001", "06088001"}),
        ("13054001,", {"13054001"}),
        ("13054001,13054001", {"13054001"}),
    ],
)
def test_parse_station_ids(value: str, expected: set[StationCode]) -> None:
    assert parse_station_ids(value) == expected


@pytest.mark.parametrize("value", ["", ",", " , ", "  "])
def test_parse_station_ids_rejects_empty(value: str) -> set[StationCode]:
    with pytest.raises(argparse.ArgumentTypeError):
        parse_station_ids(value)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Date d'ouverture : 01/01/1957", "1957-01-01T00:00:00+00:00"),
        ("DATE D'OUVERTURE : 15/03/2010", "2010-03-15T00:00:00+00:00"),
        ("No creation date here", None),
    ],
)
def test_extract_creation_date(text: str, expected: str | None) -> None:
    assert extract_creation_date(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Date de fermeture : 01/01/1957", "1957-01-01T00:00:00+00:00"),
        ("DATE DE FERMETURE : 15/03/2010", "2010-03-15T00:00:00+00:00"),
        ("Date de fermeture : Ouvert", None),
        ("No closure date here", None),
    ],
)
def test_extract_closure_date(text: str, expected: str | None) -> str:
    assert extract_closure_date(text) == expected


@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("01/09/1920", "1920-09-01T00:00:00+00:00"),
        ("15/03/2010", "2010-03-15T00:00:00+00:00"),
        ("31/12/1999", "1999-12-31T00:00:00+00:00"),
    ],
)
def test_date_dd_mm_yyyy_to_iso(date_str: str, expected: str) -> None:
    assert date_dd_mm_yyyy_to_iso(date_str) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Département : Hauts-de-Seine (92)", {"nom": "Hauts-de-Seine", "code": "92"}),
        ("Département : Corse-du-Sud (2A)", {"nom": "Corse-du-Sud", "code": "2"}),
        ("Département : Haute-Corse (2B)", {"nom": "Haute-Corse", "code": "2"}),
        (
            "Département : Provence-Alpes-Côte d'Azur",
            {"nom": "Provence-Alpes-Côte d'Azur", "code": None},
        ),
        ("DÉPARTEMENT : PARIS (75)", {"nom": "PARIS", "code": "75"}),
        ("No departement information", {"nom": None, "code": None}),
        ("Département : Seine-et-Marne  (77)", {"nom": "Seine-et-Marne", "code": "77"}),
    ],
)
def test_extract_departement(text: str, expected: dict) -> None:
    assert extract_departement(text) == expected


def test_extract_classes_one_with_debut_fin() -> None:
    text = """
QUALITE DU SITE
Paramètre Classe(*) Réf. Début Fin Méthode Date du relevé
Temperature 2 Nr35 13/12/2010 26/06/2015 1 13/12/2010
"""
    result = extract_classes(text)
    expected = [
        TemperatureClass(
            classe="2",
            debut="2010-12-13T00:00:00+00:00",
            fin="2015-06-26T00:00:00+00:00",
        )
    ]
    assert result == expected


def test_extract_classes_two_with_debut_fin() -> None:
    text = """
QUALITE DU SITE
Paramètre Classe(*) Réf. Début Fin Méthode Date du relevé
Temperature 3 Nr35 01/01/2000 31/12/2010 1 01/01/2000
Temperature 2 Nr35 01/01/2011 31/12/2020 1 01/01/2011
"""
    result = extract_classes(text)
    expected = [
        TemperatureClass(
            classe="3",
            debut="2000-01-01T00:00:00+00:00",
            fin="2010-12-31T00:00:00+00:00",
        ),
        TemperatureClass(
            classe="2",
            debut="2011-01-01T00:00:00+00:00",
            fin="2020-12-31T00:00:00+00:00",
        ),
    ]
    assert result == expected


def test_extract_classes_one_with_debut_but_no_fin() -> None:
    text = """
QUALITE DU SITE
Paramètre Classe(*) Réf. Début Fin Méthode Date du relevé
Temperature 1 Nr35B 01/01/2021 3 07/01/2026
"""
    result = extract_classes(text)
    expected = [
        TemperatureClass(classe="1", debut="2021-01-01T00:00:00+00:00", fin=None)
    ]
    assert result == expected


def test_extract_classes_one_with_debut_fin_and_one_with_debut_but_no_fin() -> None:
    text = """
QUALITE DU SITE
Paramètre Classe(*) Réf. Début Fin Méthode Date du relevé
Temperature 2 Nr35 01/01/2011 31/12/2020 1 01/01/2011
Temperature 1 Nr35B 01/01/2021 3 07/01/2026
"""
    result = extract_classes(text)
    expected = [
        TemperatureClass(
            classe="2",
            debut="2011-01-01T00:00:00+00:00",
            fin="2020-12-31T00:00:00+00:00",
        ),
        TemperatureClass(classe="1", debut="2021-01-01T00:00:00+00:00", fin=None),
    ]
    assert result == expected


def test_extract_classes_no_match() -> None:
    result = extract_classes("No quality data here")
    expected = []
    assert result == expected


def test_extract_classes_temperature_with_surrounding_text() -> None:
    text = """
QUALITE DU SITE
Humidite 1 Nr35B 03/07/2020 3 07/01/2026
Temperature 1 Nr35B 01/09/1999 3 07/01/2026
Pluie 2 Nr35B 27/06/2015 3 07/01/2026
"""
    result = extract_classes(text)
    expected = [
        TemperatureClass(classe="1", debut="1999-09-01T00:00:00+00:00", fin=None)
    ]
    assert result == expected


def test_extract_from_real_text_example() -> None:
    text = """
13054001
MARIGNANE
MARIGNANE AEROPORT - PARC
Editée le 23/03/2026
Données du 23/03/2026 à 09:33 UTC
LOCALISATION
Département: BOUCHES-DU-RHONE(13)
Date d'ouverture: 01/09/1920
QUALITE DU SITE
Paramètre Classe(*) Réf. Début Fin Méthode Date du relevé Commentaire
Humidite 1 Nr35B 03/07/2020 3 07/01/2026
Page 1 - Fiche du poste 13054001
QUALITE DU SITE
Paramètre Classe(*) Réf. Début Fin Méthode Date du relevé Commentaire
Rugosite_o 2 Nr35B 29/07/2010 1 07/01/2026
Rugosite_s 2 Nr35B 29/07/2010 1 07/01/2026
Temperature 1 Nr35B 01/09/1999 3 07/01/2026
Vent 1 Nr35B 01/09/1999 3 07/01/2026 VENT NORD
CLASSE MESURES
"""

    actual = {
        "creation_date": extract_creation_date(text),
        "closure_date": extract_closure_date(text),
        "departement": extract_departement(text),
        "classes": extract_classes(text),
    }
    expected = {
        "creation_date": "1920-09-01T00:00:00+00:00",
        "closure_date": None,
        "departement": {"nom": "BOUCHES-DU-RHONE", "code": "13"},
        "classes": [
            TemperatureClass(classe="1", debut="1999-09-01T00:00:00+00:00", fin=None)
        ],
    }

    assert actual == expected


def test_build_csv_lines_single_class() -> None:
    station = StationCode("13054001")
    info = StationInfo(
        station_code=station,
        url="https://example.com/file.pdf",
        departement="75",
        creation_date="1999-01-01T00:00:00+00:00",
        closure_date="2020-12-31T00:00:00+00:00",
        classes_temperature=[
            TemperatureClass(classe="1", debut="1999-09-01T00:00:00+00:00", fin=None)
        ],
    )
    result = build_csv_lines(station, info)
    expected = [
        [
            "13054001",
            "https://example.com/file.pdf",
            "75",
            "1999-01-01T00:00:00+00:00",
            "2020-12-31T00:00:00+00:00",
            "1",
            "1999-09-01T00:00:00+00:00",
            None,
        ]
    ]
    assert result == expected


def test_build_csv_lines_multiple_classes() -> None:
    station = StationCode("06088001")
    info = StationInfo(
        station_code=station,
        url="https://example.com/file.pdf",
        departement="06",
        creation_date="1998-01-01T00:00:00+00:00",
        closure_date=None,
        classes_temperature=[
            TemperatureClass(classe="1", debut="2000-01-01T00:00:00+00:00", fin=None),
            TemperatureClass(
                classe="2",
                debut="2015-03-15T00:00:00+00:00",
                fin="2020-06-30T00:00:00+00:00",
            ),
        ],
    )
    result = build_csv_lines(station, info)
    expected = [
        [
            "06088001",
            "https://example.com/file.pdf",
            "06",
            "1998-01-01T00:00:00+00:00",
            None,
            "1",
            "2000-01-01T00:00:00+00:00",
            None,
        ],
        [
            "06088001",
            "https://example.com/file.pdf",
            "06",
            "1998-01-01T00:00:00+00:00",
            None,
            "2",
            "2015-03-15T00:00:00+00:00",
            "2020-06-30T00:00:00+00:00",
        ],
    ]
    assert result == expected


def test_build_csv_lines_with_none_values() -> None:
    station = StationCode("14137001")
    info = StationInfo(
        station_code=station,
        url="https://example.com/file.pdf",
        departement=None,
        creation_date=None,
        closure_date=None,
        classes_temperature=[TemperatureClass(classe=None, debut=None, fin=None)],
    )
    result = build_csv_lines(station, info)
    expected = [
        ["14137001", "https://example.com/file.pdf", None, None, None, None, None, None]
    ]
    assert result == expected


def test_build_classes_csv_lines_multiple_classes() -> None:
    station = StationCode("06088001")
    info = StationInfo(
        station_code=station,
        url="https://example.com/file.pdf",
        departement="06",
        creation_date="1998-01-01T00:00:00+00:00",
        closure_date=None,
        classes_temperature=[
            TemperatureClass(classe="1", debut="2000-01-01T00:00:00+00:00", fin=None),
            TemperatureClass(
                classe="2",
                debut="2015-03-15T00:00:00+00:00",
                fin="2020-06-30T00:00:00+00:00",
            ),
        ],
    )
    result = build_classes_csv_lines(station, info)
    expected = [
        ["06088001", "1", "2000-01-01T00:00:00+00:00", None],
        ["06088001", "2", "2015-03-15T00:00:00+00:00", "2020-06-30T00:00:00+00:00"],
    ]
    assert result == expected


def test_build_lifecycle_csv_line() -> None:
    station = StationCode("06088001")
    info = StationInfo(
        station_code=station,
        url="https://example.com/file.pdf",
        departement="06",
        creation_date="1998-01-01T00:00:00+00:00",
        closure_date="2020-06-30T00:00:00+00:00",
        classes_temperature=[
            TemperatureClass(classe="1", debut="2000-01-01T00:00:00+00:00", fin=None)
        ],
    )
    result = [station, info.creation_date, info.closure_date]
    expected = ["06088001", "1998-01-01T00:00:00+00:00", "2020-06-30T00:00:00+00:00"]
    assert result == expected


def test_build_station_info_from_text_with_merignane_text_example() -> None:
    station_id = "13054001"
    pdf_url = "https://object.files.data.gouv.fr/meteofrance/data/synchro_ftp/BASE/INFOS_POSTES/13/13054001_13_MARIGNANE.pdf"

    result = build_station_info_from_text(station_id, pdf_url, MERIGNANE_TEXT_EXAMPLE)
    expected = StationInfo(
        station_code=station_id,
        url=pdf_url,
        departement="13",
        creation_date="1920-09-01T00:00:00+00:00",
        closure_date=None,
        classes_temperature=[
            TemperatureClass(classe="1", debut="1999-09-01T00:00:00+00:00", fin=None)
        ],
    )

    assert result == expected


MERIGNANE_TEXT_EXAMPLE = """
13054001
MARIGNANE
MARIGNANE AEROPORT - PARC
Editée le 23/03/2026
Données du 23/03/2026 à 09:33 UTC
Emplacement du poste, plan au 1:13542
LOCALISATION
Département: BOUCHES-DU-RHONE(13)
Commune: MARIGNANE
Lieu-dit: MARIGNANE AEROPORT -
PARC
Latitude: 43°26'13" Nord
Longitude: 5°12'41" Est
Date localisation: 13/12/2010
Altitude: 6 m
Date d'ouverture: 01/09/1920
Date de fermeture: Ouvert
EMPLACEMENTS SUCCESSIFS
Lieu_dit (lat,lon,altitude) du au
LA GALAGOVIERE (43°25'06" Nord, 5°13'15" Est, 18 m) 01/09/1920 14/03/1923
VILLA DU PIN (43°25'18" Nord, 5°13'33" Est, 6 m) 15/03/1923 30/11/1925
ROSE DES VENTS (43°25'50" Nord, 5°12'30" Est, 10 m) 01/12/1925 31/05/1940
HANGAR CAQUOT (43°26'00" Nord, 5°12'00" Est, 2 m) 01/06/1940 18/07/1943
PAVILLON MEDICAL (43°26'00" Nord, 5°13'00" Est, 2 m) 15/09/1944 28/03/1945
PAVILLON MEDICAL (43°27'00" Nord, 5°14'00" Est, 7 m) 29/03/1945 21/11/1946
MARIGNANE AEROPORT - STATION METEO (43°26'19" Nord, 5°12'26" Est, 3 m) 22/11/1946 15/11/1960
MARIGNANE AEROPORT - STATION METEO (43°26'25" Nord, 5°13'02" Est, 4 m) 16/11/1960 06/10/1981
MARIGNANE AEROPORT - BLOC TECHNIQUE (43°26'18" Nord, 5°13'24" Est, 6 m) 07/10/1981 13/12/2010
MARIGNANE AEROPORT - BLOC TECHNIQUE (43°26'16" Nord, 5°12'58" Est, 9 m) 14/12/2010 07/01/2026
MARIGNANE AEROPORT - PARC (43°26'13" Nord, 5°12'41" Est, 6 m) 08/01/2026
QUALITE DU SITE
Paramètre Classe(*) Réf. Début Fin Méthode Date du relevé Commentaire
Humidite 1 Nr35B 03/07/2020 3 07/01/2026
Humidite 3 Nr35B 27/06/2015 02/07/2020 1 26/06/2015
Humidite 1 Nr35B 01/09/1999 26/06/2015 3 26/06/2015
Pluie 2 Nr35B 27/06/2015 3 07/01/2026
Pluie 1 Nr35 01/09/1999 26/06/2015 3 29/07/2010
Ray_glo_diff 1 Nr35B 27/06/2015 3 07/01/2026
Concerne le nouveau parc situé à proximité des
Ray_glo_diff 2 Nr35 13/12/2010 26/06/2015 1 13/12/2010
pistes
Ray_glo_diff 3 Nr35 01/09/1999 12/12/2010 3 29/07/2010 Arbres et haies à proximité
Rugosite_e 2 Nr35B 27/06/2015 1 07/01/2026
Rugosite_e 2 Nr35 29/07/2010 26/06/2015 1 29/07/2010
Rugosite_n 1 Nr35B 27/06/2015 1 07/01/2026
Rugosite_n 1 Nr35 29/07/2010 26/06/2015 1 29/07/2010
Page 1 - Fiche du poste 13054001
QUALITE DU SITE
Paramètre Classe(*) Réf. Début Fin Méthode Date du relevé Commentaire
Rugosite_o 2 Nr35B 29/07/2010 1 07/01/2026
Rugosite_s 2 Nr35B 29/07/2010 1 07/01/2026
Temperature 1 Nr35B 01/09/1999 3 07/01/2026
Vent 1 Nr35B 01/09/1999 3 07/01/2026 VENT NORD
CLASSE MESURES
Paramètre Classe(**) Ref. Début Fin Date du relevé Commentaire
Humidite B NS/162/07 02/11/2007 02/11/2007
remplacement platine pluvio PM 3030 1000cm² par PM 3070
Pluie B NS/162/07 19/05/2009 19/05/2009
1000cm²
Pluie B NS/162/07 02/11/2007 18/05/2009 02/11/2007
Pression B NS/162/07 02/11/2007 02/11/2007
Rayonnement A NS/162/07 02/11/2007 02/11/2007
Tempe_a B NS/162/07 02/11/2007 02/11/2007
Tempe_s B NS/162/07 02/11/2007 02/11/2007
Temperature B NS/162/07 02/11/2007 02/11/2007
Vent B NS/162/07 02/11/2007 02/11/2007
Visibilite B NS/162/07 02/11/2007 02/11/2007
INSTRUMENTS
Capteur Début Fin Modèle H. capteur Alti. Lat_dg Lon_dg
ABRI METEO 25/02/1968 12/12/2010 Abri grand modèle BM0 1150/1151
"""
