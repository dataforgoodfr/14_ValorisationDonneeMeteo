import calendar


def clamp_day_to_month_end(year: int, month: int, day: int) -> int:
    """
    Clamp un jour au dernier jour valide du mois.
    Exemple : 30 février 2024 -> 29
    """
    last_day = calendar.monthrange(year, month)[1]
    return min(day, last_day)
