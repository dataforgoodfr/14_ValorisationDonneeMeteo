<template>
    <div class="flex flex-col gap-2">
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

        <svg
            :width="width"
            :height="height"
            :viewBox="`0 0 ${width} ${height}`"
        >
            <defs>
                <clipPath id="france-clip">
                    <path
                        v-for="f in featuresDEP"
                        :key="f.properties?.code"
                        :d="geoPath(f) ?? ''"
                    />
                </clipPath>

                <filter
                    id="heatmap-blur"
                    x="-30%"
                    y="-30%"
                    width="160%"
                    height="160%"
                    color-interpolation-filters="sRGB"
                >
                    <feGaussianBlur in="SourceGraphic" stdDeviation="20" />
                </filter>

                <linearGradient
                    id="legend-gradient"
                    x1="0"
                    x2="1"
                    y1="0"
                    y2="0"
                >
                    <stop
                        v-for="stop in legendStops"
                        :key="stop.offset"
                        :offset="stop.offset"
                        :stop-color="stop.color"
                    />
                </linearGradient>
            </defs>

            <rect :width="width" :height="height" fill="#202d43" />

            <!-- Mode points : fond avec contours -->
            <g v-if="activeMode === 'points'">
                <path
                    v-for="f in featuresDEP"
                    :key="f.properties?.code"
                    :d="geoPath(f) ?? ''"
                    fill="#202d43"
                    stroke="white"
                    stroke-width="0.4"
                />
                <path
                    v-for="f in featuresREG"
                    :key="f.properties?.code"
                    :d="geoPath(f) ?? ''"
                    fill="none"
                    stroke="white"
                    stroke-width="0.8"
                />
            </g>

            <!-- Mode heatmap : cercles flous clippés sur la France -->
            <g v-if="activeMode === 'heatmap'">
                <g clip-path="url(#france-clip)" filter="url(#heatmap-blur)">
                    <circle
                        v-for="(s, i) in projectedStations"
                        :key="i"
                        :cx="s.x"
                        :cy="s.y"
                        r="50"
                        :fill="s.color"
                        opacity="0.9"
                    />
                </g>
                <path
                    v-for="f in featuresDEP"
                    :key="f.properties?.code"
                    :d="geoPath(f) ?? ''"
                    fill="none"
                    stroke="rgba(255,255,255,0.5)"
                    stroke-width="0.4"
                />
                <path
                    v-for="f in featuresREG"
                    :key="f.properties?.code"
                    :d="geoPath(f) ?? ''"
                    fill="none"
                    stroke="white"
                    stroke-width="0.9"
                />
            </g>

            <!-- Mode points : cercles stations -->
            <g v-if="activeMode === 'points'" clip-path="url(#france-clip)">
                <circle
                    v-for="(s, i) in projectedStations"
                    :key="i"
                    :cx="s.x"
                    :cy="s.y"
                    r="3"
                    :fill="s.color"
                    stroke="rgba(255,255,255,0.5)"
                    stroke-width="0.4"
                />
            </g>

            <!-- Légende -->
            <g :transform="`translate(${legendX}, ${height - footer + 20})`">
                <text
                    :x="legendW / 2"
                    y="-6"
                    text-anchor="middle"
                    fill="white"
                    font-size="11"
                    font-family="sans-serif"
                >
                    Écart à la normale (°C)
                </text>
                <rect
                    x="0"
                    y="0"
                    :width="legendW"
                    :height="legendH"
                    :rx="legendH / 2"
                    fill="url(#legend-gradient)"
                />
                <rect
                    x="0"
                    y="0"
                    :width="legendW"
                    :height="legendH"
                    :rx="legendH / 2"
                    fill="none"
                    stroke="rgba(255,255,255,0.4)"
                    stroke-width="0.5"
                />
                <text
                    x="0"
                    :y="legendH + 14"
                    text-anchor="start"
                    fill="white"
                    font-size="11"
                    font-family="sans-serif"
                >
                    {{ DEVIATION_MIN }}°C
                </text>
                <text
                    :x="legendW"
                    :y="legendH + 14"
                    text-anchor="end"
                    fill="white"
                    font-size="11"
                    font-family="sans-serif"
                >
                    +{{ DEVIATION_MAX }}°C
                </text>
            </g>
        </svg>
    </div>
</template>

<script setup lang="ts">
import * as d3 from "d3";
import * as topojson from "topojson-client";
import type { Feature, FeatureCollection, Geometry } from "geojson";
import type { Topology, GeometryCollection } from "topojson-specification";
import type { DeviationMapParams, DeviationMapStation } from "~/types/api";

interface DepartmentProperties {
    code: string;
}

type FranceTopology = Topology<{
    DEP: GeometryCollection<DepartmentProperties>;
    REG: GeometryCollection<DepartmentProperties>;
}>;

type GeoFeature = Feature<Geometry, DepartmentProperties>;

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

const width = 500;
const height = 500;
const mapPadding = 10;
const footer = 80;
const legendH = 14;
const legendW = (width - (mapPadding + 20) * 2) / 2;
const legendX = mapPadding + 20 + (width - (mapPadding + 20) * 2) / 4;

const DEVIATION_MIN = -8;
const DEVIATION_MAX = 8;

const legendStops = Array.from({ length: 11 }, (_, i) => ({
    offset: `${i * 10}%`,
    color: d3.interpolateRdYlBu(1 - i / 10),
}));

function colorForDeviation(deviation: number): string {
    const t = Math.max(
        0,
        Math.min(
            1,
            (deviation - DEVIATION_MIN) / (DEVIATION_MAX - DEVIATION_MIN),
        ),
    );
    return d3.interpolateRdYlBu(1 - t);
}

const featuresDEP = ref<GeoFeature[]>([]);
const featuresREG = ref<GeoFeature[]>([]);
const projection = shallowRef<d3.GeoProjection | null>(null);

const geoPath = computed(() => {
    if (!projection.value) return (_: GeoFeature) => null;
    return d3.geoPath().projection(projection.value);
});

interface ProjectedStation {
    x: number;
    y: number;
    color: string;
}

const projectedStations = computed<ProjectedStation[]>(() => {
    if (!projection.value || !stationsData.value?.stations) return [];
    return stationsData.value.stations
        .filter(
            (s): s is DeviationMapStation & { lat: number; lon: number } =>
                s.lat != null && s.lon != null,
        )
        .flatMap((s) => {
            const coords = projection.value!([s.lon, s.lat]);
            if (!coords) return [];
            return [
                {
                    x: coords[0],
                    y: coords[1],
                    color: colorForDeviation(s.deviation),
                },
            ];
        });
});

onMounted(async () => {
    const res = await fetch("/json/France_2024_WGS84_DEP.json");
    const topoData = (await res.json()) as FranceTopology;

    const geojsonREG = topojson.feature(topoData, topoData.objects.REG);
    const geojsonDEP = topojson.feature(topoData, topoData.objects.DEP);

    const DOM_REG_CODES = ["01", "02", "03", "04", "06"];
    featuresDEP.value = geojsonDEP.features.filter(
        (f) => !f.properties.code.startsWith("97"),
    );
    featuresREG.value = geojsonREG.features.filter(
        (f) => !DOM_REG_CODES.includes(f.properties.code),
    );

    const mapExtent: [[number, number], [number, number]] = [
        [mapPadding, mapPadding],
        [width - mapPadding, height - mapPadding - footer],
    ];
    const featureCollection: FeatureCollection<Geometry, DepartmentProperties> =
        {
            type: "FeatureCollection",
            features: featuresDEP.value,
        };
    projection.value = d3.geoMercator().fitExtent(mapExtent, featureCollection);

    await fetchStations();
});

watch(
    params,
    async () => {
        await fetchStations();
    },
    { deep: true },
);
</script>
