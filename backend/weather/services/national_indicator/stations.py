from datetime import date

ITN_ALWAYS_STATION_CODES: frozenset[str] = frozenset(
    {
        "47091001",
        "20148001",
        "25056001",
        "33281001",
        "73054001",
        "29075001",
        "14137001",
        "36063001",
        "63113001",
        "16089001",
        "21473001",
        "72181001",
        "59343001",
        "69029001",
        "13054001",
        "26198001",
        "54526001",
        "44020001",
        "58160001",
        "06088001",
        "30189001",
        "45055001",
        "75114001",
        "64549001",
        "66136001",
        "86027001",
        "35281001",
        "67124001",
        "31069001",
    }
)

REIMS_COURCY = "51183001"
REIMS_PRUNAY = "51449002"
REIMS_SWITCH_DATE = date(2012, 5, 8)  # à partir de là: Prunay


def expected_reims_code(day: date) -> str:
    return REIMS_PRUNAY if day >= REIMS_SWITCH_DATE else REIMS_COURCY


def expected_station_codes(day: date) -> frozenset[str]:
    """
    Retourne exactement les 30 codes station attendus pour ce jour.
    (29 always + 1 Reims selon la date)
    """
    return ITN_ALWAYS_STATION_CODES | {expected_reims_code(day)}


ITN_STATION_CODES_FOR_QUERY: tuple[str, ...] = tuple(
    ITN_ALWAYS_STATION_CODES | {REIMS_COURCY, REIMS_PRUNAY}
)
