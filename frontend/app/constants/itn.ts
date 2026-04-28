import { TEMPERATURE_COLORS } from "./colors";
export const ITN_SERIES = {
    temperature: "ITN",
    baseline: "ITN des normales",
    extremes: "Extrêmes",
    stdDev: "Écart-type",
};

const ITN_LIGHT_COLORS = {
    extremes: "rgba(100, 100, 100, 0.20)",
    ecartType: "rgba(175, 175, 175, 1)",
    hotBand: TEMPERATURE_COLORS.hot,
    coldBand: TEMPERATURE_COLORS.cold,
    temperatureLine: "#999",
    baselineLine: "#333",
};

const ITN_DARK_COLORS = {
    extremes: "rgb(132, 145, 167, 0.2)",
    ecartType: "rgb(132, 145, 167, 0.5)",
    hotBand: TEMPERATURE_COLORS.hot,
    coldBand: TEMPERATURE_COLORS.cold,
    temperatureLine: "#bbbbbb",
    baselineLine: "#ccc",
};

export function useItnColors() {
    const cm = useColorMode();
    return computed(() =>
        cm.value === "dark" ? ITN_DARK_COLORS : ITN_LIGHT_COLORS,
    );
}
