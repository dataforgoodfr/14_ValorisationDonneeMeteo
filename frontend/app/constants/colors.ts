export const TEMPERATURE_COLORS = {
    cold: "#1976D2",
    hot: "#d32F2F",
};

const DARK_COLORS = {
    background: "#202d43",
    foreground: "#6690a7",
    transparent: "#202d4300",
    cold: TEMPERATURE_COLORS.cold,
    hot: TEMPERATURE_COLORS.hot,
};
const LIGHT_COLORS = {
    background: "#FFFFFF",
    foreground: "#000000",
    transparent: "#ffffff00",
    cold: TEMPERATURE_COLORS.cold,
    hot: TEMPERATURE_COLORS.hot,
};

export function useMapColors() {
    const cm = useColorMode();
    return computed(() => (cm.value === "dark" ? DARK_COLORS : LIGHT_COLORS));
}

const deviationMin = -5;
const deviationMax = 5;

const deviationStops: [number, string][] = [
    [deviationMin, TEMPERATURE_COLORS.cold],
    [deviationMin * 0.6, "hsl(210, 85%, 75%)"],
    [deviationMin * 0.2, "hsl(180, 90%, 85%)"],
    [deviationMin * 0.05, "hsl(160, 95%, 90%)"],
    [0, "#ffffff"],
    [deviationMax * 0.05, "hsl(50, 96%, 90%)"],
    [deviationMax * 0.2, "hsl(30, 90%, 85%)"],
    [deviationMax * 0.6, "hsl(0, 85%, 75%)"],
    [deviationMax, TEMPERATURE_COLORS.hot],
];

export const DEVIATION_MAP_COLORS = {
    min: deviationMin,
    max: deviationMax,
    stops: deviationStops,
};

const recordsMin = -20;
const recordsMax = 40;

const recordsStops: [number, string][] = [
    [-20, TEMPERATURE_COLORS.cold],
    [-8, "hsl(210, 85%, 75%)"],
    [0, "hsl(180, 90%, 85%)"],
    [7, "hsl(160, 95%, 90%)"],
    [12, "#ffffff"],
    [18, "hsl(50, 96%, 90%)"],
    [25, "hsl(30, 90%, 85%)"],
    [33, "hsl(0, 85%, 75%)"],
    [40, TEMPERATURE_COLORS.hot],
];

export const RECORDS_MAP_COLORS = {
    min: recordsMin,
    max: recordsMax,
    stops: recordsStops,
};
