export function downloadCSV(csv: string, filename: string): void {
    const a = document.createElement("a");
    const bom = "\uFEFF"; // Force UTF-8 detection

    a.href = `data:text/csv;charset=utf-8,${encodeURIComponent(bom + csv)}`;
    a.download = filename;
    a.click();
    a.remove();
}
