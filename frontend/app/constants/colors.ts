export const COLORS = {
    background: "#FFFFFF",
    foreground: "#000000",
    negative: "#1976D2",
    positive: "#d32F2F",
};

const deviationMin = -5;
const deviationMax = 5;

const deviationStops: [number, string][] = [
    [deviationMin, COLORS.negative],
    [deviationMin * 0.6, "hsl(210, 85%, 75%)"],
    [deviationMin * 0.2, "hsl(180, 90%, 85%)"],
    [deviationMin * 0.05, "hsl(160, 95%, 90%)"],
    [0, "#ffffff"],
    [deviationMax * 0.05, "hsl(50, 96%, 90%)"],
    [deviationMax * 0.2, "hsl(30, 90%, 85%)"],
    [deviationMax * 0.6, "hsl(0, 85%, 75%)"],
    [deviationMax, COLORS.positive],
];

export const DEVIATION_MAP_COLORS = {
    min: deviationMin,
    max: deviationMax,
    stops: deviationStops,
};

const recordsMin = -20;
const recordsMax = 40;

const recordsStops: [number, string][] = [
    [-20, COLORS.negative],
    [-8, "hsl(210, 85%, 75%)"],
    [0, "hsl(180, 90%, 85%)"],
    [7, "hsl(160, 95%, 90%)"],
    [12, "#ffffff"],
    [18, "hsl(50, 96%, 90%)"],
    [25, "hsl(30, 90%, 85%)"],
    [33, "hsl(0, 85%, 75%)"],
    [40, COLORS.positive],
];

export const RECORDS_MAP_COLORS = {
    min: recordsMin,
    max: recordsMax,
    stops: recordsStops,
};
