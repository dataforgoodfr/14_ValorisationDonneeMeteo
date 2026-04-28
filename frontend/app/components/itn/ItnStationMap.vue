<template>
    <div class="relative flex-shrink-0">
        <div
            ref="mapContainer"
            class="rounded-lg overflow-hidden"
            style="width: 600px; height: 600px"
        />
    </div>
</template>

<script setup lang="ts">
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import * as topojson from "topojson-client";
import type { FeatureCollection, Geometry } from "geojson";
import type { Topology, GeometryCollection } from "topojson-specification";
import type { ItnStation } from "~/types/api";

interface DepartmentProperties {
    code: string;
}

type FranceTopology = Topology<{
    DEP: GeometryCollection<DepartmentProperties>;
    REG: GeometryCollection<DepartmentProperties>;
}>;

const props = defineProps<{
    stations: ItnStation[];
    hoveredCode: string | null;
}>();

const emit = defineEmits<{
    "update:hoveredCode": [code: string | null];
}>();

const mapContainer = ref<HTMLDivElement | null>(null);
let map: maplibregl.Map | null = null;
const mapReady = ref(false);

const popup = new maplibregl.Popup({
    closeButton: false,
    closeOnClick: false,
    offset: 10,
    className: "bg-transparent",
});

const BLANK_STYLE: maplibregl.StyleSpecification = {
    version: 8,
    sources: {},
    layers: [
        {
            id: "background",
            type: "background",
            paint: { "background-color": "transparent" },
        },
    ],
};

const DOM_REGION_CODES = ["01", "02", "03", "04", "06"];

function stationsToGeoJSON(
    stations: ItnStation[],
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
                code: s.code,
                nom: s.nom,
            },
        })),
    };
}

function setStationsData(stations: ItnStation[]) {
    if (!map) return;
    const source = map.getSource("stations-itn") as
        | maplibregl.GeoJSONSource
        | undefined;
    source?.setData(stationsToGeoJSON(stations));
}

function initLayers() {
    if (!map) return;

    map.addSource("stations-itn", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
    });

    map.addLayer({
        id: "stations-itn-base",
        type: "circle",
        source: "stations-itn",
        paint: {
            "circle-radius": 5,
            "circle-color": "#90a1b9",
        },
    });

    map.addLayer({
        id: "stations-itn-highlight",
        type: "circle",
        source: "stations-itn",
        filter: ["==", ["get", "code"], ""],
        paint: {
            "circle-radius": 8,
            // Cannot use the CSS variable here, so we hardcode the color.
            "circle-color": "#4a9fd4",
            "circle-opacity": 1,
        },
    });

    map.on("mouseenter", "stations-itn-base", (e) => {
        map!.getCanvas().style.cursor = "default";
        const feature = e.features?.[0];
        if (!feature) return;
        const { code } = feature.properties as { code: string };
        emit("update:hoveredCode", code);
    });

    map.on("mouseleave", "stations-itn-base", () => {
        map!.getCanvas().style.cursor = "";
        emit("update:hoveredCode", null);
    });
}

onMounted(async () => {
    const res = await fetch("/json/France_2024_WGS84_DEP.json");
    const topoData = (await res.json()) as FranceTopology;

    const geojsonRegion = topojson.feature(topoData, topoData.objects.REG);

    const regFeatures = geojsonRegion.features.filter(
        (f) => !DOM_REGION_CODES.includes(f.properties.code),
    );

    map = new maplibregl.Map({
        container: mapContainer.value!,
        style: BLANK_STYLE,
        center: [2.5, 46.5],
        zoom: 4,
        attributionControl: false,
        interactive: false,
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

    map.on("load", () => {
        map!.addSource("france-reg", {
            type: "geojson",
            data: { type: "FeatureCollection", features: regFeatures },
        });
        map!.addLayer({
            id: "france-reg-border",
            type: "line",
            source: "france-reg",
            paint: { "line-color": "#507087", "line-width": 1 },
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

// React when hovering over a station in the map or list.
watch(
    () => props.hoveredCode,
    (code) => {
        if (!map || !mapReady.value) {
            return;
        }
        map.setFilter("stations-itn-highlight", [
            "==",
            ["get", "code"],
            code ?? "",
        ]);

        if (!code) {
            popup.remove();
            return;
        }

        const station = props.stations.find((s) => s.code === code);
        if (!station) {
            return;
        }

        popup
            .setLngLat([station.lon, station.lat])
            .setHTML(`<span class="itn-popup-label">${station.nom}</span>`)
            .addTo(map);
    },
);
</script>

<style>
.maplibregl-popup-content {
    background: transparent;
    box-shadow: none;
    padding: 0;
}
.maplibregl-popup-tip {
    display: none;
}
.itn-popup-label {
    color: var(--color-blue-450);
    font-weight: 600;
    font-size: var(--text-s);
}
</style>
