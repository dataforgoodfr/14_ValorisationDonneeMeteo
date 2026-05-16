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

// Palette warming stripes (RdBu ColorBrewer / showyourstripes.info)
const WARMING_STRIPES = [
    "#053061",
    "#2166ac",
    "#4393c3",
    "#92c5de",
    "#d1e5f0",
    "#f7f7f7",
    "#fddbc7",
    "#f4a582",
    "#d6604d",
    "#b2182b",
    "#67001f",
];

function makeColorStops(min: number, max: number): [number, string][] {
    const n = WARMING_STRIPES.length - 1;
    return WARMING_STRIPES.map((color, i) => [
        min + (i / n) * (max - min),
        color,
    ]);
}

function makeDeviationColors(min: number, max: number): MapColorConfig {
    return { min, max, stops: makeColorStops(min, max) };
}

export const DEVIATION_MAP_COLORS = makeDeviationColors(-5, 5);
export const DEVIATION_MAP_MONTHLY_COLORS = makeDeviationColors(-10, 10);

const recordsMin = -20;
const recordsMax = 40;

export const RECORDS_MAP_COLORS = {
    min: recordsMin,
    max: recordsMax,
    stops: makeColorStops(recordsMin, recordsMax),
};

export function getMapColor(value: number, stops: [number, string][]): string {
    if (!stops.length) return "#888";
    return stops.reduce((a, b) =>
        Math.abs(b[0] - value) < Math.abs(a[0] - value) ? b : a,
    )[1];
}
