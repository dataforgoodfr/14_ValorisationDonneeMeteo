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
    return dateToStringYMD(getLastDayOfYear(date));
}

/** Format a Date as DD/MM/YYYY for display. */
export function dateToStringDMY(date: Date): string {
    return `${date.toLocaleDateString("fr-FR")}`;
}

/** Returns the first day of the year for the given date as date */
export function getFirstDayOfYear(date: Date): Date {
    return new Date(date.getUTCFullYear(), 1 - 1, 1, 0, 0, 0, 0);
}

/** Returns the first day of the year for the given date as date */
export function getFirstDayOfYearInLocal(date: Date): Date {
    return fromUTCToLocal(getFirstDayOfYear(fromLocalToUTC(date)));
}

function isCurrentYear(date: Date, today: Date = new Date()): boolean {
    return date.getFullYear() === today.getFullYear();
}

/**
 * Returns the last day of the year for the given date as date (local time)
 * otherwise, returns today minus 2 days if the year is the current year.
 */
export function getLastAvailableDayOfYear(
    date: Date,
    today: Date = new Date(),
): Date {
    return isCurrentYear(date, today)
        ? getOneDayBeforeDate(today)
        : getLastDayOfYear(date);
}

/**
 * Returns the last day of the year for the given date as date (local time)
 * otherwise, returns today minus 2 days if the year is the current year.
 */
export function getLastAvailableDayOfYearInLocal(
    date: Date,
    today: Date = new Date(),
): Date {
    return fromUTCToLocal(
        getLastAvailableDayOfYear(fromLocalToUTC(date), today),
    );
}

export function getLastDayOfYear(date: Date): Date {
    return new Date(Date.UTC(date.getUTCFullYear(), 12 - 1, 31));
}

export function getOneDayBeforeDate(date: Date): Date {
    return new Date(
        Date.UTC(
            date.getUTCFullYear(),
            date.getUTCMonth(),
            date.getUTCDate() - 1,
        ),
    );
}

/** Format a Date as day Month Year for display. */
export function formatDateLongForDisplay(d: Date): string {
    return d.toLocaleDateString("fr-FR", { dateStyle: "long" });
}

export function fromLocalToUTC(date: Date): Date {
    return new Date(
        Date.UTC(
            date.getFullYear(),
            date.getMonth(),
            date.getDate(),
            date.getHours(),
            date.getMinutes(),
            date.getSeconds(),
            date.getMilliseconds(),
        ),
    );
}

export function fromUTCToLocal(date: Date): Date {
    return new Date(
        date.getUTCFullYear(),
        date.getUTCMonth(),
        date.getUTCDate(),
        date.getUTCHours(),
        date.getUTCMinutes(),
        date.getUTCSeconds(),
        date.getUTCMilliseconds(),
    );
}
