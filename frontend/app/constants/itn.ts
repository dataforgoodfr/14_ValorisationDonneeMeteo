export const ITN_SERIES = {
    temperature: "ITN",
    baseline: "ITN des normales",
    extremes: "Extrêmes",
    stdDev: "Écart-type",
};

const ITN_LIGHT_COLORS = {
    extremes: "rgba(100, 100, 100, 0.20)",
    ecartType: "rgba(175, 175, 175, 1)",
    hotBand: "rgba(255, 50, 50, 0.55)",
    coldBand: "rgba(0, 80, 220, 0.55)",
    temperatureLine: "#999",
    baselineLine: "#333",
};

const ITN_DARK_COLORS = {
    extremes: "rgba(200, 200, 200, 0.12)",
    ecartType: "rgba(110, 110, 110, 1)",
    hotBand: "rgba(255, 100, 100, 0.50)",
    coldBand: "rgba(80, 140, 255, 0.50)",
    temperatureLine: "#bbbbbb",
    baselineLine: "#ccc",
};

export function useItnColors() {
    const cm = useColorMode();
    return computed(() =>
        cm.value === "dark" ? ITN_DARK_COLORS : ITN_LIGHT_COLORS,
    );
}
