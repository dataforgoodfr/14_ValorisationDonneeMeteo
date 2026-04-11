/** Format a Date as YYYY-MM-DD (local time). */
export function dateToStringYMD(date: Date): string {
    return `${date.toLocaleDateString("sv-SE")}`;
}

/** Returns the first day of the year for the given date as YYYY-01-01 (local time) */
export function dateToFirstDayOfYearYMD(date: Date = new Date()): string {
    return dateToStringYMD(new Date(date.getFullYear(), 0, 1));
}

/**
 * Returns the last day of the year for the given date as YYYY-12-31 (local time)
 * otherwise, returns today minus 2 days if the year is the current year.
 */
export function dateToLastDayOfYearYMD(date: Date = new Date()): string {
    const today = new Date();
    const isCurrentYear = date.getFullYear() === today.getFullYear();

    if (isCurrentYear) {
        const lastDay = new Date(today);
        lastDay.setDate(today.getDate() - 2);

        return dateToStringYMD(lastDay);
    }

    return dateToStringYMD(new Date(date.getFullYear(), 11, 31));
}

/** Format a Date as DD/MM/YYYY for display. */
export function dateToStringDMY(date: Date): string {
    return `${date.toLocaleDateString("fr-FR")}`;
}
