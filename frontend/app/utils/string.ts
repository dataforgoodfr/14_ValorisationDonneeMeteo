export function XX(n: number): string {
    return String(n).padStart(2, "0");
}

export function normalizeString(str: string): string {
    return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

export function escapeCsvValue(v: string | number | undefined): string {
    const s = String(v ?? "");
    return s.includes(",") || s.includes('"')
        ? `"${s.replace(/"/g, '""')}"`
        : s;
}
