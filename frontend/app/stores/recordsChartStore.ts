import { refDebounced } from "@vueuse/core";
import { useTemperatureRecords } from "~/composables/useTemperature";
import { dateToStringYMD } from "~/utils/date";
import type { Station } from "~/types/api";

const debounceDuration = 300;

export enum TerritoryFilterType {
    STATION = "STATION",
    DEPARTMENT = "DEPARTMENT",
    REGION = "REGION",
    TERRITORY = "TERRITORY",
}

type SelectedItem = {
    value: string;
    id: string;
    type: TerritoryFilterType;
};

export const useRecordsChartStore = defineStore("recordsChartStore", () => {
    // Date range — default to the past year
    const defaultStartDate = new Date();
    defaultStartDate.setFullYear(defaultStartDate.getFullYear() - 1);
    const startDate = ref<Date>(defaultStartDate);
    const endDate = ref<Date>(new Date());
    const departmentsFilter = ref<string[]>([]);
    const stationCodeFilter = ref<string[]>([]);
    const regionsFilter = ref<string[]>([]);
    const territoriesFilter = ref<string[]>(["FR"]);
    const selectedElements = ref<SelectedItem[]>([
        {
            id: "FR",
            value: "France Métropolitaine",
            type: TerritoryFilterType.TERRITORY,
        },
    ]);

    // Pagination
    const page = ref(1);
    const pageSize = ref(3);

    // Debounced values used to drive API calls
    const debouncedStartDate = refDebounced(startDate, debounceDuration);
    const debouncedEndDate = refDebounced(endDate, debounceDuration);
    const debouncedDepartmentsFilter = refDebounced(
        departmentsFilter,
        debounceDuration,
    );
    const debouncedStationCodeFilter = refDebounced(
        stationCodeFilter,
        debounceDuration,
    );

    const params = computed(() => ({
        date_start: dateToStringYMD(debouncedStartDate.value),
        date_end: dateToStringYMD(debouncedEndDate.value),
        limit: pageSize.value,
        offset: (page.value - 1) * pageSize.value,
        departement_filter: debouncedDepartmentsFilter.value.join(","),
        station_name_filter: debouncedStationCodeFilter.value.join(","),
    }));

    function setDepartmentFilter(department: { code: string; name: string }) {
        if (departmentsFilter.value.includes(department.code)) {
            return;
        }
        departmentsFilter.value.push(department.code);
        selectedElements.value.push({
            id: department.code,
            value: `${department.name} (${department.code})`,
            type: TerritoryFilterType.DEPARTMENT,
        });
    }

    function setStationFilter(station: Station) {
        if (stationCodeFilter.value.includes(station.code)) {
            return;
        }
        stationCodeFilter.value.push(station.code);
        selectedElements.value.push({
            id: station.code,
            value: `${station.nom} (${station.departement})`,
            type: TerritoryFilterType.STATION,
        });
    }

    function setRegionFilter(region: { code: string; name: string }) {
        if (regionsFilter.value.includes(region.code)) {
            return;
        }
        regionsFilter.value.push(region.code);
        selectedElements.value.push({
            id: region.code,
            value: region.name,
            type: TerritoryFilterType.REGION,
        });
    }

    function setTerritoryFilter(territory: { code: string; name: string }) {
        if (territoriesFilter.value.includes(territory.code)) {
            return;
        }
        territoriesFilter.value.push(territory.code);
        selectedElements.value.push({
            id: territory.code,
            value: territory.name,
            type: TerritoryFilterType.TERRITORY,
        });
    }

    function removeItemFromFilter(type: TerritoryFilterType, code: string) {
        selectedElements.value = selectedElements.value.filter(
            (element) => !(element.type === type && element.id === code),
        );
        switch (type) {
            case TerritoryFilterType.DEPARTMENT:
                departmentsFilter.value = departmentsFilter.value.filter(
                    (dept) => dept !== code,
                );
                break;
            case TerritoryFilterType.STATION:
                stationCodeFilter.value = stationCodeFilter.value.filter(
                    (station) => station !== code,
                );
                break;
            case TerritoryFilterType.REGION:
                regionsFilter.value = regionsFilter.value.filter(
                    (region) => region !== code,
                );
                break;
            case TerritoryFilterType.TERRITORY:
                territoriesFilter.value = territoriesFilter.value.filter(
                    (territory) => territory !== code,
                );
                break;
        }
    }
    const { data: recordsData, pending, error } = useTemperatureRecords(params);

    return {
        startDate,
        endDate,
        setDepartmentFilter,
        setStationFilter,
        setRegionFilter,
        setTerritoryFilter,
        removeItemFromFilter,
        page,
        pageSize,
        recordsData,
        stationCodeFilter,
        departmentsFilter,
        regionsFilter,
        territoriesFilter,
        pending,
        error,
        selectedElements,
    };
});
