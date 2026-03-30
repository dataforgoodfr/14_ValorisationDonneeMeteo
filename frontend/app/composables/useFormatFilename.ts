function nowDateFormatted() {
    // Helper function to pad numbers with a leading zero
    const nowDate = new Date();
    const pad = (num: number) => num.toString().padStart(2, "0");

    const year = nowDate.getFullYear();
    const month = pad(nowDate.getMonth() + 1); // getMonth() is zero-based (0-11)
    const day = pad(nowDate.getDate());

    const hours = pad(nowDate.getHours());
    const minutes = pad(nowDate.getMinutes());
    const seconds = pad(nowDate.getSeconds());

    return `${year}${month}${day}_${hours}${minutes}${seconds}`;
}

const toISODate = (date: Date) =>
    date.toISOString().substring(0, "YYYY-MM-DD".length);

export function useFormatFileName(
    chartName: string,
    granularity: string,
    dateStart: Date,
    dateEnd: Date,
    fileFormat: string,
) {
    const fileName = `${nowDateFormatted()}_${chartName}_${granularity}_${toISODate(dateStart)}_to_${toISODate(dateEnd)}.${fileFormat}`;
    return fileName;
}
