<template>
    <div>
        <canvas
            ref="canvas"
            :width="width * dpr"
            :height="height * dpr"
            :style="{ width: width + 'px', height: height + 'px' }"
        ></canvas>
    </div>
</template>

<script>
let cachedTempMOCKED = null;
</script>

<script setup>
import { ref, onMounted } from "vue";
import * as d3 from "d3";
import * as topojson from "topojson-client";
import { storeToRefs } from "pinia";
import { useRecordsStore } from "~/stores/recordsStore";

const store = useRecordsStore();
const {
    recordType,
    startDate,
    endDate,
    page,
    pageSize,
    recordsData,
    pending,
    error,
} = storeToRefs(store);
const { getFilter, setFilter } = store;

watch(recordsData, (val) => {
    // console.log("stations :", val?.stations);
});

const props = defineProps({
    mode: {
        type: String,
        default: "points", // "points" | "heatmap" | "stations"
    },
    stationType: {
        type: Number,
        default: null,
    },
    date: {
        type: String,
        default: null,
    },
});

const width = 500;
const height = 500;
const dpr = 2;
const canvas = ref(null);
const minTemp = 0;
const maxTemp = 30;

// Génère N points aléatoires à l'intérieur des régions GeoJSON fournies
// avec une température plus élevée dans le sud (lat faible) que dans le nord
function generateTempMOCKED(n = 200, features) {
    const tempMin = 8;
    const tempMax = 21;
    const latMetroMin = 42.3;
    const latMetroMax = 51.1;
    const points = [];

    while (points.length < n) {
        const feature = features[Math.floor(Math.random() * features.length)];
        const [[lonMin, latMin], [lonMax, latMax]] = d3.geoBounds(feature);

        let attempts = 0;
        while (attempts < 50) {
            const lon = lonMin + Math.random() * (lonMax - lonMin);
            const lat = latMin + Math.random() * (latMax - latMin);
            if (d3.geoContains(feature, [lon, lat])) {
                const latNorm =
                    (lat - latMetroMin) / (latMetroMax - latMetroMin);
                const baseTemp = tempMax - latNorm * (tempMax - tempMin);
                const temp =
                    Math.round((baseTemp + (Math.random() * 4 - 2)) * 10) / 10;
                points.push({
                    lon,
                    lat,
                    temperature: Math.min(tempMax, Math.max(tempMin, temp)),
                });
                break;
            }
            attempts++;
        }
    }
    return points;
}

function drawBasemap(context, path, featuresDEP, featuresREG) {
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

function drawLegend(context, width, mapPadding, footer) {
    const legendW = (width - (mapPadding + 20) * 2) / 2;
    const legendX = mapPadding + 20 + (width - (mapPadding + 20) * 2) / 4;
    const legendY = height - footer + 20;
    const legendH = 14;

    context.fillStyle = "#ffffff";
    context.font = "11px sans-serif";
    context.textAlign = "center";
    context.fillText("Température (°C)", legendX + legendW / 2, legendY - 6);

    const gradient = context.createLinearGradient(
        legendX,
        0,
        legendX + legendW,
        0,
    );
    for (let i = 0; i <= 10; i++) {
        gradient.addColorStop(i / 10, d3.interpolateRdYlBu(1 - i / 10));
    }
    context.fillStyle = gradient;
    context.fillRect(legendX, legendY, legendW, legendH);

    context.strokeStyle = "rgba(255,255,255,0.4)";
    context.lineWidth = 0.5;
    context.strokeRect(legendX, legendY, legendW, legendH);

    context.fillStyle = "#ffffff";
    context.font = "11px sans-serif";
    context.textAlign = "left";
    context.fillText("0°C", legendX, legendY + legendH + 14);
    context.textAlign = "right";
    context.fillText("30°C", legendX + legendW, legendY + legendH + 14);
}

function drawLegendDate(context, mapPadding, date) {
    context.fillStyle = "#ffffff";
    context.font = "bold 12px sans-serif";
    context.textAlign = "left";
    context.fillText(date, mapPadding + 10, mapPadding + 15);
}

function drawPoints(context, projection, tempMOCKED) {
    tempMOCKED.forEach(({ lon, lat, temperature }) => {
        const [x, y] = projection([lon, lat]);
        context.beginPath();
        context.arc(x, y, 3, 0, 2 * Math.PI);
        context.fillStyle = d3.interpolateRdYlBu(
            1 - (temperature - minTemp) / (maxTemp - minTemp),
        );
        context.fill();
        context.strokeStyle = "rgba(255,255,255,0.5)";
        context.lineWidth = 0.4;
        context.stroke();
    });
}

function drawPointsStationsTemp(
    context,
    projection,
    infoclimatStationsTemp,
    temperatureDate = "2025-06-01",
) {
    infoclimatStationsTemp.forEach((station, i) => {
        const lon = station.lon;
        const lat = station.lat;
        const temp = station[temperatureDate];

        const [x, y] = projection([lon, lat]);
        context.beginPath();
        context.arc(x, y, 3, 0, 2 * Math.PI);
        context.fillStyle = d3.interpolateRdYlBu(
            1 - (temp - minTemp) / (maxTemp - minTemp),
        );
        context.fill();
        context.strokeStyle = "rgba(255,255,255,0.5)";
        context.lineWidth = 0.4;
        context.stroke();
    });
}

const stationTypeColor = d3
    .scaleOrdinal()
    .domain([0, 1, 2, 3, 4])
    .range(["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"]);

function drawStationsLegend(
    context,
    width,
    mapPadding,
    footer,
    stationType,
    count,
) {
    const centerX = width / 2;
    const legendY = height - footer + 20;

    context.fillStyle = "#ffffff";
    context.font = "bold 12px sans-serif";
    context.textAlign = "center";
    const typeLabel = stationType !== null ? stationType : "tous";
    context.fillText(
        `Type de station : ${typeLabel} - ${count} station${count > 1 ? "s" : ""}`,
        centerX,
        legendY + 14,
    );
}

function drawStationsPoints(context, projection, stations, filterType = null) {
    const data =
        filterType !== null
            ? stations.filter((s) => s.station_type === filterType)
            : stations;
    data.forEach(({ lon, lat, station_type }) => {
        const [x, y] = projection([lon, lat]);
        context.beginPath();
        context.arc(x, y, 1, 0, 2 * Math.PI);
        context.fillStyle =
            filterType !== null ? "#ffffff" : stationTypeColor(station_type);
        context.fill();
        context.strokeStyle = "rgba(255,255,255,0.5)";
        context.lineWidth = 0.4;
        // context.stroke();
    });
}

function drawHeatmapStationsTemp(
    context,
    projection,
    infoclimatStationsTemp,
    featuresDEP,
    featuresREG,
    path,
    footer,
    temperatureDate = "2025-06-01",
) {
    const projectedPoints = infoclimatStationsTemp
        .filter((s) => s[temperatureDate] != null)
        .map((s) => {
            const [px, py] = projection([s.lon, s.lat]);
            return { px, py, temperature: s[temperatureDate] };
        });

    const mapAreaH = height - footer;
    const offscreen = document.createElement("canvas");
    offscreen.width = width;
    offscreen.height = mapAreaH;
    const offCtx = offscreen.getContext("2d");
    const imageData = offCtx.createImageData(width, mapAreaH);

    const sigma = 40;
    const step = 1;
    for (let y = 0; y < mapAreaH; y += step) {
        for (let x = 0; x < width; x += step) {
            let sumWeight = 0;
            let sumTemp = 0;
            for (const { px, py, temperature } of projectedPoints) {
                const dist2 = (x - px) ** 2 + (y - py) ** 2;
                const w = Math.exp(-dist2 / (2 * sigma ** 2));
                sumWeight += w;
                sumTemp += w * temperature;
            }
            const temp = sumTemp / sumWeight;
            const col = d3.color(
                d3.interpolateRdYlBu(
                    1 - (temp - minTemp) / (maxTemp - minTemp),
                ),
            );
            for (let dy = 0; dy < step && y + dy < mapAreaH; dy++) {
                for (let dx = 0; dx < step && x + dx < width; dx++) {
                    const idx = ((y + dy) * width + (x + dx)) * 4;
                    imageData.data[idx] = col.r;
                    imageData.data[idx + 1] = col.g;
                    imageData.data[idx + 2] = col.b;
                    imageData.data[idx + 3] = 210;
                }
            }
        }
    }
    offCtx.putImageData(imageData, 0, 0);

    const svgPath = d3.geoPath().projection(projection);
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

    // drawPointsStationsTemp(
    //     context,
    //     projection,
    //     infoclimatStationsTemp,
    //     temperatureDate,
    // );
}

function drawHeatmap(
    context,
    projection,
    tempMOCKED,
    featuresDEP,
    featuresREG,
    path,
    footer,
) {
    const projectedPoints = tempMOCKED.map(({ lon, lat, temperature }) => {
        const [px, py] = projection([lon, lat]);
        return { px, py, temperature };
    });

    const mapAreaH = height - footer;
    const offscreen = document.createElement("canvas");
    offscreen.width = width;
    offscreen.height = mapAreaH;
    const offCtx = offscreen.getContext("2d");
    const imageData = offCtx.createImageData(width, mapAreaH);

    const sigma = 40; // rayon de lissage gaussien en pixels
    const step = 1;
    for (let y = 0; y < mapAreaH; y += step) {
        for (let x = 0; x < width; x += step) {
            let sumWeight = 0;
            let sumTemp = 0;
            for (const { px, py, temperature } of projectedPoints) {
                const dist2 = (x - px) ** 2 + (y - py) ** 2;
                // const w = dist2 < 0.25 ? 1e8 : 1 / dist2;
                const w = Math.exp(-dist2 / (2 * sigma ** 2));
                sumWeight += w;
                sumTemp += w * temperature;
            }
            const temp = sumTemp / sumWeight;
            const col = d3.color(
                d3.interpolateRdYlBu(1 - (temp - 8) / (21 - 8)),
            );
            for (let dy = 0; dy < step && y + dy < mapAreaH; dy++) {
                for (let dx = 0; dx < step && x + dx < width; dx++) {
                    const idx = ((y + dy) * width + (x + dx)) * 4;
                    imageData.data[idx] = col.r;
                    imageData.data[idx + 1] = col.g;
                    imageData.data[idx + 2] = col.b;
                    imageData.data[idx + 3] = 210;
                }
            }
        }
    }
    offCtx.putImageData(imageData, 0, 0);

    const svgPath = d3.geoPath().projection(projection);
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

    drawPoints(context, projection, tempMOCKED);
}

onMounted(async () => {
    const topoData = await fetch("/json/France_2024_WGS84_DEP.json").then(
        (res) => res.json(),
    );

    const infoclimatStations = await fetch("/data/D4G_stations.csv")
        .then((res) => res.text())
        .then((text) => d3.csvParse(text, d3.autoType));

    // console.log("infoclimatStations :", infoclimatStations);

    const infoclimatStationsTemp = await fetch(
        "/data/stations_temperatures_2024_2025.csv",
    )
        .then((res) => res.text())
        .then((text) => d3.dsvFormat(";").parse(text, d3.autoType));

    // console.log("infoclimatStationsTemp :", infoclimatStationsTemp);

    const geojsonREG = topojson.feature(topoData, topoData.objects.REG);
    const geojsonDEP = topojson.feature(topoData, topoData.objects.DEP);

    const featuresDEP = geojsonDEP.features.filter(
        (f) => !f.properties.code.startsWith("97"),
    );
    const DOM_REG_CODES = ["01", "02", "03", "04", "06"];
    const featuresREG = geojsonREG.features.filter(
        (f) => !DOM_REG_CODES.includes(f.properties.code),
    );

    if (!cachedTempMOCKED) {
        cachedTempMOCKED = generateTempMOCKED(500, featuresREG);
    }
    const tempMOCKED = cachedTempMOCKED;

    const context = canvas.value.getContext("2d");
    context.scale(dpr, dpr);

    const mapPadding = 10;
    const footer = 80;
    const map_extent = [
        [mapPadding, mapPadding],
        [width - mapPadding, height - mapPadding - footer],
    ];

    const featureCollection = {
        type: "FeatureCollection",
        features: featuresDEP,
    };
    const projection = d3
        .geoMercator()
        .fitExtent(map_extent, featureCollection);
    const path = d3.geoPath().projection(projection).context(context);

    context.clearRect(0, 0, width, height);
    context.fillStyle = "#202d43";
    context.fillRect(0, 0, width, height);

    if (props.mode === "points") {
        drawBasemap(context, path, featuresDEP, featuresREG);
        drawPoints(context, projection, tempMOCKED);
        drawLegend(context, width, mapPadding, footer);
    }
    if (props.mode === "heatmap") {
        drawHeatmap(
            context,
            projection,
            tempMOCKED,
            featuresDEP,
            featuresREG,
            path,
            footer,
        );
        drawLegend(context, width, mapPadding, footer);
    }
    if (props.mode === "stations") {
        drawBasemap(context, path, featuresDEP, featuresREG);
        drawStationsPoints(
            context,
            projection,
            infoclimatStations,
            props.stationType,
        );
        const filteredCount =
            props.stationType !== null
                ? infoclimatStations.filter(
                      (s) => s.station_type === props.stationType,
                  ).length
                : infoclimatStations.length;
        drawStationsLegend(
            context,
            width,
            mapPadding,
            footer,
            props.stationType,
            filteredCount,
        );
    }

    if (props.mode === "stationsPoints") {
        drawBasemap(context, path, featuresDEP, featuresREG);
        // console.log("props.date :", props.date);
        drawPointsStationsTemp(
            context,
            projection,
            infoclimatStationsTemp,
            props.date,
        );
        drawLegend(context, width, mapPadding, footer);
        drawLegendDate(context, mapPadding, props.date);
    }

    if (props.mode === "heatmapStationsTemp") {
        drawHeatmapStationsTemp(
            context,
            projection,
            infoclimatStationsTemp,
            featuresDEP,
            featuresREG,
            path,
            footer,
            props.date,
        );
        drawLegend(context, width, mapPadding, footer);
        drawLegendDate(context, mapPadding, props.date);
    }
});
</script>
