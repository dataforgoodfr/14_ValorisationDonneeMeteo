function formatDateManually(date: Date) {
    // Helper function to pad numbers with a leading zero
    const pad = (num: number) => num.toString().padStart(2, "0");

    const year = date.getFullYear();
    const month = pad(date.getMonth() + 1); // getMonth() is zero-based (0-11)
    const day = pad(date.getDate());

    const hours = pad(date.getHours());
    const minutes = pad(date.getMinutes());
    const seconds = pad(date.getSeconds());

    return `${year}${month}${day}_${hours}${minutes}${seconds}`;
}

export function useFormatFileName(
    granularity: string,
    interval: string,
    chartName: string,
) {
    // Helper function to format exported file name
    const now = new Date(Date.now());
    return `${formatDateManually(now)}_${chartName}_${granularity}_${interval}`;
}
