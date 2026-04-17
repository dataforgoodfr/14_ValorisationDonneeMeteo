<template>
    <div class="flex flex-col gap-2 w-[500px] flex-shrink-0">
        <div class="flex flex-col gap-0.5">
            <div class="flex items-baseline gap-2">
                <span class="text-sm text-muted">Écart à la normale moyen</span>
                <span
                    v-if="nationalDeviation != null"
                    class="text-lg font-semibold"
                    :class="
                        nationalDeviation >= 0
                            ? 'text-red-400'
                            : 'text-blue-400'
                    "
                >
                    {{ nationalDeviation >= 0 ? "+" : ""
                    }}{{ nationalDeviation.toFixed(1) }} °C
                </span>
                <span v-else class="text-lg font-semibold text-muted">—</span>
            </div>
            <div class="text-xs text-muted">
                <span v-if="baseline"
                    >Période des normales : {{ baseline }}</span
                >
                <span v-if="baseline"> · </span>
                en France métropolitaine
            </div>
        </div>

        <USelect
            v-model="activeMode"
            :items="modeOptions"
            value-key="value"
            label-key="label"
            size="sm"
            class="w-full"
        />

        <div class="relative">
            <div
                ref="mapContainer"
                class="w-full rounded-lg overflow-hidden"
                style="height: 480px"
            />
            <div
                class="absolute bottom-4 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 pointer-events-none"
            >
                <span class="text-xs text-white/80"
                    >Écart à la normale (°C)</span
                >
                <div
                    class="rounded-full"
                    :style="{
                        width: '160px',
                        height: '12px',
                        background: `linear-gradient(to right, ${LEGEND_GRADIENT})`,
                    }"
                />
                <div class="flex justify-between w-full text-xs text-white/70">
                    <span>{{ DEVIATION_MIN }}°C</span>
                    <span>+{{ DEVIATION_MAX }}°C</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import * as topojson from "topojson-client";
import type { FeatureCollection, Geometry, Point } from "geojson";
import type { Topology, GeometryCollection } from "topojson-specification";
import type { DeviationMapParams, DeviationMapStation } from "~/types/api";
import { formatDeviationMapTooltip } from "~/components/charts/tooltipFormatters/deviationMapTooltipFormatter";

interface DepartmentProperties {
    code: string;
}

type FranceTopology = Topology<{
    DEP: GeometryCollection<DepartmentProperties>;
    REG: GeometryCollection<DepartmentProperties>;
}>;

const props = withDefaults(
    defineProps<{
        mode?: "points" | "heatmap";
        dateStart: string;
        dateEnd: string;
    }>(),
    { mode: "points" },
);

const activeMode = ref<"points" | "heatmap">(props.mode);
const modeOptions = [
    { label: "Stations", value: "points" },
    { label: "Carte de chaleur", value: "heatmap" },
];

const DEVIATION_MIN = -8;
const DEVIATION_MAX = 8;

// RdYlBu-like stops: cold=blue, neutral=yellow, hot=red
const COLOR_STOPS: [number, string][] = [
    [-8, "#3288bd"],
    [-4, "#99d594"],
    [-1, "#e6f598"],
    [0, "#ffffbf"],
    [1, "#fee08b"],
    [4, "#fc8d59"],
    [8, "#d53e4f"],
];

const LEGEND_GRADIENT = COLOR_STOPS.map(([, color]) => color).join(", ");

// MapLibre interpolate expression for circle-color / heatmap-weight
const deviationColorExpr: maplibregl.ExpressionSpecification = [
    "interpolate",
    ["linear"],
    ["get", "deviation"],
    ...COLOR_STOPS.flat(),
];

// ─── Data ────────────────────────────────────────────────────────────────────

const params = computed<DeviationMapParams>(() => ({
    date_start: props.dateStart,
    date_end: props.dateEnd,
    limit: 500,
}));

const { data: stationsData, execute: fetchStations } =
    useTemperatureDeviationMap(params, `deviation-map-${props.mode}`);

const nationalDeviation = computed(
    () => stationsData.value?.national.deviation_mean ?? null,
);
const baseline = computed(() => {
    const b = stationsData.value?.metadata.baseline;
    if (!b) return null;
    return b.replace("-", " – ");
});

// ─── MapLibre ────────────────────────────────────────────────────────────────

const mapContainer = ref<HTMLDivElement | null>(null);
let map: maplibregl.Map | null = null;

const BLANK_STYLE: maplibregl.StyleSpecification = {
    version: 8,
    sources: {},
    layers: [
        {
            id: "background",
            type: "background",
            paint: { "background-color": "#202d43" },
        },
    ],
};

const DOM_REG_CODES = ["01", "02", "03", "04", "06"];

function stationsToGeoJSON(
    stations: DeviationMapStation[],
): FeatureCollection<Geometry> {
    return {
        type: "FeatureCollection",
        features: stations
            .filter((s) => s.lat != null && s.lon != null)
            .map((s) => ({
                type: "Feature",
                geometry: {
                    type: "Point",
                    coordinates: [s.lon as number, s.lat as number],
                },
                properties: {
                    deviation: s.deviation,
                    station_name: s.station_name,
                },
            })),
    };
}

function setStationsData(stations: DeviationMapStation[]) {
    if (!map) return;
    const source = map.getSource("stations") as
        | maplibregl.GeoJSONSource
        | undefined;
    source?.setData(stationsToGeoJSON(stations));
}

function syncLayerVisibility() {
    if (!map) return;
    map.setLayoutProperty(
        "stations-circles",
        "visibility",
        activeMode.value === "points" ? "visible" : "none",
    );
    map.setLayoutProperty(
        "stations-heatmap-blur",
        "visibility",
        activeMode.value === "heatmap" ? "visible" : "none",
    );
}

function addTooltipEvents(layerId: string) {
    if (!map) return;
    const popup = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
        offset: 8,
    });

    map.on("mouseenter", layerId, (e) => {
        map!.getCanvas().style.cursor = "pointer";
        const feature = e.features?.[0];
        if (!feature) return;
        const { station_name, deviation } = feature.properties as {
            station_name: string;
            deviation: number;
        };
        const coords = (feature.geometry as Point).coordinates.slice() as [
            number,
            number,
        ];
        popup
            .setLngLat(coords)
            .setHTML(formatDeviationMapTooltip(station_name, deviation))
            .addTo(map!);
    });

    map.on("mouseleave", layerId, () => {
        map!.getCanvas().style.cursor = "";
        popup.remove();
    });
}

function initLayers() {
    if (!map) return;

    map.addSource("stations", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
    });

    // Points layer
    map.addLayer({
        id: "stations-circles",
        type: "circle",
        source: "stations",
        layout: { visibility: "visible" },
        paint: {
            "circle-radius": 5,
            "circle-color": deviationColorExpr,
            "circle-stroke-width": 0.5,
            "circle-stroke-color": "rgba(255,255,255,0.5)",
            "circle-opacity": 0.9,
        },
    });

    // Heatmap layer — large blurry circles colored by actual deviation value
    map.addLayer({
        id: "stations-heatmap-blur",
        type: "circle",
        source: "stations",
        layout: { visibility: "none" },
        paint: {
            "circle-radius": 35,
            "circle-color": deviationColorExpr,
            "circle-blur": 1,
            "circle-opacity": 0.35,
        },
    });

    addTooltipEvents("stations-circles");
    addTooltipEvents("stations-heatmap-blur");

    syncLayerVisibility();
}

onMounted(async () => {
    const res = await fetch("/json/France_2024_WGS84_DEP.json");
    const topoData = (await res.json()) as FranceTopology;

    const geojsonDEP = topojson.feature(topoData, topoData.objects.DEP);
    const geojsonREG = topojson.feature(topoData, topoData.objects.REG);

    const depFeatures = geojsonDEP.features.filter(
        (f) => !f.properties.code.startsWith("97"),
    );
    const regFeatures = geojsonREG.features.filter(
        (f) => !DOM_REG_CODES.includes(f.properties.code),
    );

    map = new maplibregl.Map({
        container: mapContainer.value!,
        style: BLANK_STYLE,
        center: [2.5, 46.5],
        zoom: 4,
        minZoom: 3,
        maxZoom: 9,
        maxBounds: [
            [-7, 40],
            [12, 53],
        ],
        attributionControl: false,
        interactive: true,
    });

    map.once("load", () => {
        map!.resize();
        // Fit to mainland France bounds with padding
        map!.fitBounds(
            [
                [-5.2, 41.3],
                [9.6, 51.1],
            ],
            { padding: 20, duration: 0 },
        );
    });

    map.on("load", async () => {
        // France departments fill
        map!.addSource("france-dep", {
            type: "geojson",
            data: { type: "FeatureCollection", features: depFeatures },
        });
        map!.addLayer({
            id: "france-dep-fill",
            type: "fill",
            source: "france-dep",
            paint: { "fill-color": "#202d43", "fill-opacity": 1 },
        });
        map!.addLayer({
            id: "france-dep-border",
            type: "line",
            source: "france-dep",
            paint: {
                "line-color": "rgba(255,255,255,0.35)",
                "line-width": 0.5,
            },
        });

        // Region borders (thicker)
        map!.addSource("france-reg", {
            type: "geojson",
            data: { type: "FeatureCollection", features: regFeatures },
        });
        map!.addLayer({
            id: "france-reg-border",
            type: "line",
            source: "france-reg",
            paint: {
                "line-color": "rgba(255,255,255,0.8)",
                "line-width": 1,
            },
        });

        initLayers();

        await fetchStations();
        setStationsData(stationsData.value?.stations ?? []);
    });
});

onUnmounted(() => {
    map?.remove();
    map = null;
});

watch(
    params,
    async () => {
        await fetchStations();
        setStationsData(stationsData.value?.stations ?? []);
    },
    { deep: true },
);

watch(
    () => stationsData.value?.stations,
    (stations) => {
        if (stations) setStationsData(stations);
    },
);

watch(activeMode, syncLayerVisibility);
</script>
