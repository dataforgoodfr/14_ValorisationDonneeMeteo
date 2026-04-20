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

        <div class="relative">
            <div
                ref="mapContainer"
                class="w-full rounded-lg overflow-hidden"
                style="height: 480px"
            />
            <div
                class="absolute bottom-4 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 pointer-events-none"
            >
                <span class="text-xs" :style="{ color: COLORS.foreground }"
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
                <div
                    class="flex justify-between w-full text-xs"
                    :style="{ color: COLORS.foreground }"
                >
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
import { COLORS, DEVIATION_MAP_COLORS } from "~/constants/colors";

interface DepartmentProperties {
    code: string;
}

type FranceTopology = Topology<{
    DEP: GeometryCollection<DepartmentProperties>;
    REG: GeometryCollection<DepartmentProperties>;
}>;

const DEVIATION_MIN = DEVIATION_MAP_COLORS.min;
const DEVIATION_MAX = DEVIATION_MAP_COLORS.max;

const LEGEND_GRADIENT = DEVIATION_MAP_COLORS.stops
    .map(([, color]) => color)
    .join(", ");

const deviationColorExpr: maplibregl.ExpressionSpecification = [
    "interpolate",
    ["linear"],
    ["get", "deviation"],
    ...DEVIATION_MAP_COLORS.stops.flat(),
];

// ─── Data ────────────────────────────────────────────────────────────────────

const props = defineProps<{
    dateStart: string;
    dateEnd: string;
}>();

const params = computed<DeviationMapParams>(() => ({
    date_start: props.dateStart,
    date_end: props.dateEnd,
    limit: 99999,
}));

const { data: stationsData, execute: fetchStations } =
    useTemperatureDeviationMap(params, "deviation-map");

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
            paint: { "background-color": COLORS.background },
        },
    ],
};

const DOM_REGION_CODES = ["01", "02", "03", "04", "06"];

function stationsToGeoJSON(
    stations: DeviationMapStation[],
): FeatureCollection<Geometry> {
    return {
        type: "FeatureCollection",
        features: stations.map((s) => ({
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

function initLayers() {
    if (!map) return;

    map.addSource("stations", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
    });

    map.addLayer({
        id: "stations-circles",
        type: "circle",
        source: "stations",
        paint: {
            "circle-radius": 3,
            "circle-color": deviationColorExpr,
            "circle-stroke-width": 0.5,
            "circle-stroke-color": "rgba(255,255,255,0.5)",
            "circle-opacity": 0.9,
        },
    });

    const popup = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: false,
        offset: 8,
    });

    map.on("mouseenter", "stations-circles", (e) => {
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

    map.on("mouseleave", "stations-circles", () => {
        map!.getCanvas().style.cursor = "";
        popup.remove();
    });
}

onMounted(async () => {
    const res = await fetch("/json/France_2024_WGS84_DEP.json");
    const topoData = (await res.json()) as FranceTopology;

    const geojsonDepartment = topojson.feature(topoData, topoData.objects.DEP);
    const geojsonRegion = topojson.feature(topoData, topoData.objects.REG);

    const depFeatures = geojsonDepartment.features.filter(
        (f) => !f.properties.code.startsWith("97"),
    );
    const regFeatures = geojsonRegion.features.filter(
        (f) => !DOM_REGION_CODES.includes(f.properties.code),
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
        map!.fitBounds(
            [
                [-5.2, 41.3],
                [9.6, 51.1],
            ],
            { padding: 40, duration: 0 },
        );
    });

    map.on("load", async () => {
        map!.addSource("france-dep", {
            type: "geojson",
            data: { type: "FeatureCollection", features: depFeatures },
        });
        map!.addLayer({
            id: "france-dep-fill",
            type: "fill",
            source: "france-dep",
            paint: {
                "fill-color": COLORS.background,
                "fill-opacity": 1,
            },
        });
        map!.addLayer({
            id: "france-dep-border",
            type: "line",
            source: "france-dep",
            paint: {
                "line-color": COLORS.foreground,
                "line-width": 0.3,
            },
        });

        map!.addSource("france-reg", {
            type: "geojson",
            data: { type: "FeatureCollection", features: regFeatures },
        });
        map!.addLayer({
            id: "france-reg-border",
            type: "line",
            source: "france-reg",
            paint: {
                "line-color": COLORS.foreground,
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
</script>
