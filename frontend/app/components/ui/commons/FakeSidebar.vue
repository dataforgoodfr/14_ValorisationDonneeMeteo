<script setup lang="ts">
const selectedStations = ref<string[]>(["Paris", "Lyon"]);

const stations = [
    "Paris",
    "Lyon",
    "Marseille",
    "Toulouse",
    "Nice",
    "Nantes",
    "Strasbourg",
    "Montpellier",
];

function isStationSelected(station: string) {
    return selectedStations.value.includes(station);
}

function toggleStation(station: string) {
    if (isStationSelected(station)) {
        selectedStations.value = selectedStations.value.filter(
            (s) => s !== station,
        );
    } else {
        selectedStations.value = [...selectedStations.value, station];
    }
}
</script>

<template>
    <div class="w-64 p-4 flex flex-col gap-4">
        <div class="flex flex-col gap-2">
            <h3 class="text-sm font-semibold text-highlighted">Stations</h3>
            <div class="flex flex-col gap-1.5">
                <UCheckbox
                    v-for="station in stations"
                    :key="station"
                    :model-value="isStationSelected(station)"
                    :label="station"
                    @update:model-value="toggleStation(station)"
                />
            </div>
        </div>

        <UButton color="neutral" block> Appliquer les filtres </UButton>
    </div>
</template>
