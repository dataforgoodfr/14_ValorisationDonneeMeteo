import type { MapColorConfig } from "~/types/api";

export const TEMPERATURE_COLORS = {
    cold: "#1976D2",
    hot: "#d32F2F",
};

export function useMapColors() {
    const DARK_COLORS = {
        background: "#202d43",
        foreground: "#6690a7",
        transparent: "#202d4300",
        cold: TEMPERATURE_COLORS.cold,
        hot: TEMPERATURE_COLORS.hot,
        splitLine: "rgba(255, 255, 255, 0.08)",
        chartAccentColor: "#3a5080",
        loadingSpinColor: "#3b82f6",
    };
    const LIGHT_COLORS = {
        background: "#FFFFFF",
        foreground: "#000000",
        transparent: "#ffffff00",
        cold: TEMPERATURE_COLORS.cold,
        hot: TEMPERATURE_COLORS.hot,
        splitLine: "rgba(0, 0, 0, 0.12)",
        chartAccentColor: "#3a5080",
        loadingSpinColor: "#3b82f6",
    };

    const cm = useColorMode();
    return computed(() => (cm.value === "dark" ? DARK_COLORS : LIGHT_COLORS));
}

function makeDeviationColors(min: number, max: number): MapColorConfig {
    const stops: [number, string][] = [
        [min, TEMPERATURE_COLORS.cold],
        [min * 0.6, "hsl(210, 85%, 75%)"],
        [min * 0.2, "hsl(180, 90%, 85%)"],
        [min * 0.05, "hsl(160, 95%, 90%)"],
        [0, "#ffffff"],
        [max * 0.05, "hsl(50, 96%, 90%)"],
        [max * 0.2, "hsl(30, 90%, 85%)"],
        [max * 0.6, "hsl(0, 85%, 75%)"],
        [max, TEMPERATURE_COLORS.hot],
    ];
    return { min, max, stops };
}

export const DEVIATION_MAP_COLORS = makeDeviationColors(-5, 5);
export const DEVIATION_MAP_MONTHLY_COLORS = makeDeviationColors(-10, 10);

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
