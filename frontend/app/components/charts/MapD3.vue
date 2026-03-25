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

<script setup>
import { ref, onMounted } from "vue";
import * as d3 from "d3";
import * as topojson from "topojson-client";

const width = 600;
const height = 600;
const dpr = 2;
const canvas = ref(null);

// Génère N points aléatoires à l'intérieur des régions GeoJSON fournies
// avec une température plus élevée dans le sud (lat faible) que dans le nord
function generateTempMOCKED(n = 200, features) {
    const tempMin = 8;
    const tempMax = 21;
    const latMetroMin = 42.3;
    const latMetroMax = 51.1;
    const points = [];

    while (points.length < n) {
        // Choisir une région aléatoire
        const feature = features[Math.floor(Math.random() * features.length)];
        const [[lonMin, latMin], [lonMax, latMax]] = d3.geoBounds(feature);

        // Tenter de trouver un point à l'intérieur de la région
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

onMounted(async () => {
    // Charger le GeoJSON
    const topoData = await fetch("/json/France_2024_WGS84_DEP.json").then(
        (res) => res.json(),
    );
    console.log(topoData);

    // Convertir le TopoJSON en GeoJSON
    const geojsonREG = topojson.feature(topoData, topoData.objects.REG);
    const geojsonDEP = topojson.feature(topoData, topoData.objects.DEP);

    // Filtrer les DOM (codes commençant par "97")
    const featuresDEP = geojsonDEP.features.filter(
        (f) => !f.properties.code.startsWith("97"),
    );

    const DOM_REG_CODES = ["01", "02", "03", "04", "06"];
    const featuresREG = geojsonREG.features.filter(
        (f) => !DOM_REG_CODES.includes(f.properties.code),
    );

    const tempMOCKED = generateTempMOCKED(500, featuresREG);

    console.log(geojsonREG);
    console.log(geojsonDEP);

    // Créer le contexte du canvas
    const context = canvas.value.getContext("2d");
    context.scale(dpr, dpr);

    let mapPadding = 10;
    let footer = 80;

    let map_extent = [
        [mapPadding, mapPadding],
        [width - mapPadding, height - mapPadding - footer],
    ];

    // Projection basée sur les features filtrées
    const featureCollection = {
        type: "FeatureCollection",
        features: featuresDEP,
    };
    const projection = d3
        .geoMercator()
        .fitExtent(map_extent, featureCollection);
    const path = d3.geoPath().projection(projection).context(context);

    // Dessiner la carte
    context.clearRect(0, 0, width, height);

    // Fond de carte
    context.fillStyle = "#202d43";
    context.fillRect(0, 0, width, height);

    // Style des départements
    context.strokeStyle = "#ffffff";
    context.lineWidth = 0.4;
    context.fillStyle = "#202d43";

    featuresDEP.forEach((feature) => {
        context.beginPath();
        path(feature);
        context.fill();
        context.stroke();
    });

    // Style des régions
    context.strokeStyle = "#ffffff";
    context.lineWidth = 0.8;
    context.fillStyle = "#202d43";

    featuresREG.forEach((feature) => {
        context.beginPath();
        path(feature);
        // context.fill();
        context.stroke();
    });

    // Dessiner les points tempMOCKED
    tempMOCKED.forEach(({ lon, lat, temperature }) => {
        const [x, y] = projection([lon, lat]);
        context.beginPath();
        context.arc(x, y, 3, 0, 2 * Math.PI);
        context.fillStyle = d3.interpolateRdYlBu(
            1 - (temperature - 8) / (21 - 8),
        );
        context.fill();
        context.strokeStyle = "rgba(255,255,255,0.5)";
        context.lineWidth = 0.4;
        // context.stroke();
    });

    // Légende : gradient RdYlBu en bas de carte
    const legendW = width - (mapPadding + 20) * 2;
    const legendX = mapPadding + 20;
    const legendY = height - footer + 20;
    const legendH = 14;

    // Titre au-dessus de la barre
    context.fillStyle = "#ffffff";
    context.font = "11px sans-serif";
    context.textAlign = "center";
    context.fillText("Température (°C)", legendX + legendW / 2, legendY - 6);

    // Gradient RdYlBu
    const gradient = context.createLinearGradient(
        legendX,
        0,
        legendX + legendW,
        0,
    );
    for (let i = 0; i <= 10; i++) {
        const t = i / 10;
        gradient.addColorStop(t, d3.interpolateRdYlBu(1 - t));
    }
    context.fillStyle = gradient;
    context.fillRect(legendX, legendY, legendW, legendH);

    // Bordure du rectangle
    context.strokeStyle = "rgba(255,255,255,0.4)";
    context.lineWidth = 0.5;
    context.strokeRect(legendX, legendY, legendW, legendH);

    // Labels min / max
    context.fillStyle = "#ffffff";
    context.font = "11px sans-serif";
    context.textAlign = "left";
    context.fillText("8°C", legendX, legendY + legendH + 14);
    context.textAlign = "right";
    context.fillText("21°C", legendX + legendW, legendY + legendH + 14);
});
</script>
