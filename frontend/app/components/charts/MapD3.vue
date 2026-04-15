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

        <canvas
            ref="canvas"
            :width="width * dpr"
            :height="height * dpr"
            :style="{ width: width + 'px', height: height + 'px' }"
        ></canvas>
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
const dpr = 2;
const mapPadding = 10;
const footer = 80;

const canvas = ref<HTMLCanvasElement | null>(null);

let featuresDEP: GeoFeature[] = [];
let featuresREG: GeoFeature[] = [];
let projection: d3.GeoProjection | null = null;
let pathFn: d3.GeoPath | null = null;
let ctxRef: CanvasRenderingContext2D | null = null;

/** Fixed scale [-8, 8]°C as per design spec. Values outside this range are clamped. */
const DEVIATION_MIN = -8;
const DEVIATION_MAX = 8;

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

function drawBasemap(
    context: CanvasRenderingContext2D,
    path: d3.GeoPath,
): void {
    context.strokeStyle = "#ffffff";
    context.lineWidth = 0.4;
    context.fillStyle = "#202d43";
    featuresDEP.forEach((feature) => {
        context.beginPath();
        path(feature);
        context.fill();
        context.stroke();
    });
    context.strokeStyle = "#ffffff";
    context.lineWidth = 0.8;
    featuresREG.forEach((feature) => {
        context.beginPath();
        path(feature);
        context.stroke();
    });
}

function drawLegend(context: CanvasRenderingContext2D): void {
    const legendW = (width - (mapPadding + 20) * 2) / 2;
    const legendX = mapPadding + 20 + (width - (mapPadding + 20) * 2) / 4;
    const legendY = height - footer + 20;
    const legendH = 14;

    context.fillStyle = "#ffffff";
    context.font = "11px sans-serif";
    context.textAlign = "center";
    context.fillText(
        "Écart à la normale (°C)",
        legendX + legendW / 2,
        legendY - 6,
    );

    const gradient = context.createLinearGradient(
        legendX,
        0,
        legendX + legendW,
        0,
    );
    for (let i = 0; i <= 10; i++) {
        gradient.addColorStop(i / 10, d3.interpolateRdYlBu(1 - i / 10));
    }
    const radius = legendH / 2;
    context.beginPath();
    context.roundRect(legendX, legendY, legendW, legendH, radius);
    context.fillStyle = gradient;
    context.fill();

    context.beginPath();
    context.roundRect(legendX, legendY, legendW, legendH, radius);
    context.strokeStyle = "rgba(255,255,255,0.4)";
    context.lineWidth = 0.5;
    context.stroke();

    context.fillStyle = "#ffffff";
    context.font = "11px sans-serif";
    context.textAlign = "left";
    context.fillText(`${DEVIATION_MIN}°C`, legendX, legendY + legendH + 14);
    context.textAlign = "right";
    context.fillText(
        `+${DEVIATION_MAX}°C`,
        legendX + legendW,
        legendY + legendH + 14,
    );
}

function drawPoints(
    context: CanvasRenderingContext2D,
    stations: DeviationMapStation[],
    proj: d3.GeoProjection,
): void {
    stations.forEach(({ lon, lat, deviation }) => {
        if (lon == null || lat == null) return;
        const coords = proj([lon, lat]);
        if (!coords) return;
        const [x, y] = coords;
        context.beginPath();
        context.arc(x, y, 3, 0, 2 * Math.PI);
        context.fillStyle = colorForDeviation(deviation);
        context.fill();
        context.strokeStyle = "rgba(255,255,255,0.5)";
        context.lineWidth = 0.4;
        context.stroke();
    });
}

function drawHeatmap(
    context: CanvasRenderingContext2D,
    stations: DeviationMapStation[],
    path: d3.GeoPath,
    proj: d3.GeoProjection,
): void {
    const projectedPoints = stations
        .filter(
            (s): s is DeviationMapStation & { lat: number; lon: number } =>
                s.lat != null && s.lon != null,
        )
        .flatMap((s) => {
            const coords = proj([s.lon, s.lat]);
            if (!coords) return [];
            const [px, py] = coords;
            return [{ px, py, deviation: s.deviation }];
        });

    const mapAreaH = height - footer;
    const offscreen = document.createElement("canvas");
    offscreen.width = width;
    offscreen.height = mapAreaH;
    const offCtx = offscreen.getContext("2d")!;
    const imageData = offCtx.createImageData(width, mapAreaH);

    const sigma = 40;
    for (let y = 0; y < mapAreaH; y++) {
        for (let x = 0; x < width; x++) {
            let sumWeight = 0;
            let sumDev = 0;
            for (const { px, py, deviation } of projectedPoints) {
                const dist2 = (x - px) ** 2 + (y - py) ** 2;
                const w = Math.exp(-dist2 / (2 * sigma ** 2));
                sumWeight += w;
                sumDev += w * deviation;
            }
            const dev = sumDev / sumWeight;
            const col = d3.rgb(colorForDeviation(dev));
            const idx = (y * width + x) * 4;
            imageData.data[idx] = col.r;
            imageData.data[idx + 1] = col.g;
            imageData.data[idx + 2] = col.b;
            imageData.data[idx + 3] = 210;
        }
    }
    offCtx.putImageData(imageData, 0, 0);

    const svgPath = d3.geoPath().projection(proj);
    const clipPath = new Path2D();
    featuresDEP.forEach((feature) => {
        const d = svgPath(feature);
        if (d) clipPath.addPath(new Path2D(d));
    });
    context.save();
    context.clip(clipPath);
    context.drawImage(offscreen, 0, 0);
    context.restore();

    context.strokeStyle = "rgba(255,255,255,0.5)";
    context.lineWidth = 0.4;
    featuresDEP.forEach((feature) => {
        context.beginPath();
        path(feature);
        context.stroke();
    });
    context.strokeStyle = "#ffffff";
    context.lineWidth = 0.9;
    featuresREG.forEach((feature) => {
        context.beginPath();
        path(feature);
        context.stroke();
    });
}

function draw(): void {
    if (!ctxRef || !projection || !pathFn) return;
    const stations = stationsData.value?.stations;
    if (!stations) return;

    ctxRef.clearRect(0, 0, width, height);
    ctxRef.fillStyle = "#202d43";
    ctxRef.fillRect(0, 0, width, height);

    if (activeMode.value === "points") {
        drawBasemap(ctxRef, pathFn);
        drawPoints(ctxRef, stations, projection);
        drawLegend(ctxRef);
    }
    if (activeMode.value === "heatmap") {
        drawHeatmap(ctxRef, stations, pathFn, projection);
        drawLegend(ctxRef);
    }
}

onMounted(async () => {
    const res = await fetch("/json/France_2024_WGS84_DEP.json");
    const topoData = (await res.json()) as FranceTopology;

    const geojsonREG = topojson.feature(topoData, topoData.objects.REG);
    const geojsonDEP = topojson.feature(topoData, topoData.objects.DEP);

    const DOM_REG_CODES = ["01", "02", "03", "04", "06"];
    featuresDEP = geojsonDEP.features.filter(
        (f) => !f.properties.code.startsWith("97"),
    );
    featuresREG = geojsonREG.features.filter(
        (f) => !DOM_REG_CODES.includes(f.properties.code),
    );

    const mapExtent: [[number, number], [number, number]] = [
        [mapPadding, mapPadding],
        [width - mapPadding, height - mapPadding - footer],
    ];
    const featureCollection: FeatureCollection<Geometry, DepartmentProperties> =
        {
            type: "FeatureCollection",
            features: featuresDEP,
        };
    projection = d3.geoMercator().fitExtent(mapExtent, featureCollection);

    ctxRef = canvas.value!.getContext("2d")!;
    ctxRef.scale(dpr, dpr);
    pathFn = d3.geoPath().projection(projection).context(ctxRef);

    await fetchStations();
    draw();
});

watch(
    params,
    async () => {
        await fetchStations();
        draw();
    },
    { deep: true },
);
watch(
    stationsData,
    (data) => {
        if (data) draw();
    },
    { deep: true },
);
watch(activeMode, draw);
</script>
