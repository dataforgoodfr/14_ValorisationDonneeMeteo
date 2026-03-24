/** Format a Date as YYYY-MM-DD (local time). */
export function dateToStr(d: Date): string {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/** Parse a YYYY-MM-DD string into a local Date. */
export function strToDate(s: string): Date {
    const [y, m, d] = s.split("-").map(Number);
    return new Date(y, m - 1, d);
}

/** Format a YYYY-MM-DD string as DD/MM/YYYY for display. */
export function formatDateForDisplay(s: string): string {
    const [y, m, d] = s.split("-");
    return `${d}/${m}/${y}`;
}
