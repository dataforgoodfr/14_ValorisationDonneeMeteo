/** Format a Date as YYYY-MM-DD (local time). */
export function dateToStringYMD(date: Date): string {
    return `${date.toLocaleDateString("sv-SE")}`;
}

/** Format a Date as DD/MM/YYYY for display. */
export function dateToStringDMY(date: Date): string {
    return `${date.toLocaleDateString("fr-FR")}`;
}
