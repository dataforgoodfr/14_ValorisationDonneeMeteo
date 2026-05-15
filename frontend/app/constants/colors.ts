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

function hexToRgb(hex: string): [number, number, number] {
    return [
        parseInt(hex.slice(1, 3), 16),
        parseInt(hex.slice(3, 5), 16),
        parseInt(hex.slice(5, 7), 16),
    ];
}

function rgbToHex(r: number, g: number, b: number): string {
    return `#${[r, g, b]
        .map((v) => Math.round(v).toString(16).padStart(2, "0"))
        .join("")}`;
}

export function interpolateMapColor(
    value: number,
    stops: [number, string][],
): string {
    if (stops.length === 0) return "#000000";
    const first = stops[0]!;
    const last = stops[stops.length - 1]!;
    if (value <= first[0]) return first[1];
    if (value >= last[0]) return last[1];

    let i = 0;
    while (i < stops.length - 1 && stops[i + 1]![0] <= value) i++;

    const [v0, c0] = stops[i]!;
    const [v1, c1] = stops[i + 1]!;
    const t = (value - v0) / (v1 - v0);
    const [r0, g0, b0] = hexToRgb(c0);
    const [r1, g1, b1] = hexToRgb(c1);
    return rgbToHex(r0 + (r1 - r0) * t, g0 + (g1 - g0) * t, b0 + (b1 - b0) * t);
}
