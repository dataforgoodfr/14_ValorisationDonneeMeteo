<template>
    <div class="relative">
        <div
            ref="mapContainer"
            class="w-full rounded-lg overflow-hidden"
            style="height: 700px"
        />
        <div
            class="absolute bottom-4 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 pointer-events-none"
        >
            <span class="text-xs" :style="{ color: mapColors.foreground }">{{
                legendLabel
            }}</span>
            <div
                class="rounded-full"
                :style="{
                    width: '160px',
                    height: '12px',
                    background: `linear-gradient(to right, ${legendGradient})`,
                }"
            />
            <div
                class="flex justify-between w-full text-xs"
                :style="{ color: mapColors.foreground }"
            >
                <span>{{ colorConfig.min }}°C</span>
                <span
                    >{{ colorConfig.max > 0 ? "+" : ""
                    }}{{ colorConfig.max }}°C</span
                >
            </div>
        </div>
        <MapAttribution class="mt-2" />
    </div>
</template>

<script setup lang="ts">
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import * as topojson from "topojson-client";
import type { FeatureCollection, Geometry, Point } from "geojson";
import type { GeometryCollection, Topology } from "topojson-specification";
import type {
    MapColorConfig,
    MappableStation,
    MapTooltipFormatter,
} from "~/types/api";
import { useMapColors } from "~/constants/colors";

const mapColors = useMapColors();

interface DepartmentProperties {
    code: string;
}

type FranceTopology = Topology<{
    DEP: GeometryCollection<DepartmentProperties>;
    REG: GeometryCollection<DepartmentProperties>;
}>;

const props = defineProps<{
    stations: MappableStation[];
    colorConfig: MapColorConfig;
    tooltipFormatter: MapTooltipFormatter;
    legendLabel: string;
}>();

const legendGradient = computed(() =>
    props.colorConfig.stops.map(([, color]) => color).join(", "),
);

const mapContainer = ref<HTMLDivElement | null>(null);
let map: maplibregl.Map | null = null;
const mapReady = ref(false);

const BLANK_STYLE: maplibregl.StyleSpecification = {
    version: 8,
    sources: {},
    layers: [
        {
            id: "background",
            type: "background",
            paint: { "background-color": mapColors.value.transparent },
        },
    ],
};

const DOM_REGION_CODES = ["01", "02", "03", "04", "06"];

function stationsToGeoJSON(
    stations: MappableStation[],
): FeatureCollection<Geometry> {
    return {
        type: "FeatureCollection",
        features: stations.map((s) => ({
            type: "Feature",
            geometry: {
                type: "Point",
                coordinates: [s.lon, s.lat],
            },
            properties: {
                station_name: s.station_name,
                value: s.value,
                record_date: s.record_date ?? null,
                department: s.department ?? null,
            },
        })),
    };
}

function setStationsData(stations: MappableStation[]) {
    if (!map) return;
    const source = map.getSource("stations") as
        | maplibregl.GeoJSONSource
        | undefined;
    source?.setData(stationsToGeoJSON(stations));
}

function initLayers() {
    if (!map) return;

    const colorExpr: maplibregl.ExpressionSpecification = [
        "interpolate",
        ["linear"],
        ["get", "value"],
        ...props.colorConfig.stops.flat(),
    ];

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
            "circle-color": colorExpr,
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
        const properties = feature.properties as {
            station_name: string;
            value: number;
            record_date: string | null;
            department: string | null;
        };
        const coords = (feature.geometry as Point).coordinates.slice() as [
            number,
            number,
        ];
        popup
            .setLngLat(coords)
            .setHTML(props.tooltipFormatter(properties))
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

    map.addControl(
        new maplibregl.NavigationControl({ showCompass: false }),
        "top-right",
    );

    map.addControl(
        {
            onAdd(m) {
                const el = document.createElement("div");
                el.className = "maplibregl-ctrl maplibregl-ctrl-group";
                const btn = document.createElement("button");
                btn.type = "button";
                btn.title = "Réinitialiser la vue";
                btn.setAttribute("aria-label", "Réinitialiser la vue");
                btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="29" height="20" viewBox="0 0 20 20" fill="none"><path d="M3 7V3h4M17 7V3h-4M3 13v4h4M17 13v4h-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
                btn.onclick = () =>
                    m.fitBounds(
                        [
                            [-5.2, 41.3],
                            [9.6, 51.1],
                        ],
                        {
                            padding: {
                                top: 50,
                                right: 50,
                                bottom: 50,
                                left: 40,
                            },
                            duration: 500,
                        },
                    );
                el.appendChild(btn);
                return el;
            },
            onRemove() {},
        },
        "top-right",
    );

    map.once("load", () => {
        map!.resize();
        map!.fitBounds(
            [
                [-5.2, 41.3],
                [9.6, 51.1],
            ],
            {
                padding: { top: -10, right: 50, bottom: 50, left: 40 },
                duration: 0,
            },
        );
    });

    map.on("load", () => {
        map!.addSource("france-dep", {
            type: "geojson",
            data: { type: "FeatureCollection", features: depFeatures },
        });
        map!.addLayer({
            id: "france-dep-fill",
            type: "fill",
            source: "france-dep",
            paint: {
                "fill-color": mapColors.value.transparent,
                "fill-opacity": 1,
            },
        });
        map!.addLayer({
            id: "france-dep-border",
            type: "line",
            source: "france-dep",
            paint: {
                "line-color": mapColors.value.foreground,
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
                "line-color": mapColors.value.foreground,
                "line-width": 1,
            },
        });

        initLayers();
        mapReady.value = true;
        setStationsData(props.stations);
    });
});

onUnmounted(() => {
    map?.remove();
    map = null;
});

watch(
    () => props.stations,
    (stations) => {
        if (mapReady.value) setStationsData(stations);
    },
);

watch(mapColors, (colors) => {
    if (!map || !mapReady.value) return;
    map.setPaintProperty("background", "background-color", colors.transparent);
    map.setPaintProperty("france-dep-fill", "fill-color", colors.transparent);
    map.setPaintProperty("france-dep-border", "line-color", colors.foreground);
    map.setPaintProperty("france-reg-border", "line-color", colors.foreground);
});
</script>
