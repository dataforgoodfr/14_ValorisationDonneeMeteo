import { refDebounced } from "@vueuse/core";
import { useTemperatureRecordsChartFake } from "~/composables/useTemperatureRecordsChart.fake";
import { dateToStringYMD } from "~/utils/date";
import type { Station, TemperatureRecordsParams } from "~/types/api";
import type {
    GranularityType,
    SliceType,
    ChartType,
} from "~/components/ui/commons/selectBar/types";

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

export const useRecordsChartStore = defineStore("recordChartStore", () => {
    const recordsChartRef = shallowRef();

    const pickedDateStart = ref(new Date(1950, 0, 1));
    const pickedDateEnd = ref(new Date());

    const debouncedDateStart = refDebounced(pickedDateStart, debounceDuration);
    const debouncedDateEnd = refDebounced(pickedDateEnd, debounceDuration);

    const granularity = ref<GranularityType>("year");
    const sliceTypeSwitchEnabled = ref(false);
    const sliceType = ref<SliceType>("full");
    const sliceDatepickerDate = ref(new Date(2006, 0, 1));
    const chartTypeSwitchEnabled = ref(false);
    const chartType = ref<ChartType>("pyramid");

    const stationCodeFilter = ref<string[]>([]);
    const departmentsFilter = ref<string[]>([]);
    const regionsFilter = ref<string[]>([]);
    const territoriesFilter = ref<string[]>([]);
    const selectedElements = ref<SelectedItem[]>([]);

    const debouncedDepartmentsFilter = refDebounced(
        departmentsFilter,
        debounceDuration,
    );
    const debouncedStationCodeFilter = refDebounced(
        stationCodeFilter,
        debounceDuration,
    );

    const params = computed<TemperatureRecordsParams>(() => ({
        date_start: dateToStringYMD(debouncedDateStart.value),
        date_end: dateToStringYMD(debouncedDateEnd.value),
        ...(debouncedStationCodeFilter.value.length > 0
            ? { station_ids: debouncedStationCodeFilter.value.join(",") }
            : {}),
        ...(debouncedDepartmentsFilter.value.length > 0
            ? { departments: debouncedDepartmentsFilter.value.join(",") }
            : {}),
    }));

    const {
        data: recordsData,
        pending,
        error,
    } = useTemperatureRecordsChartFake(params);

    const setGranularity = (value: GranularityType) => {
        sliceType.value = "full";
        granularity.value = value;
        if (value === "day") sliceTypeSwitchEnabled.value = false;
    };

    const setChartType = (value: ChartType) => {
        chartType.value = value;
    };

    function setDepartmentFilter(department: { code: string; name: string }) {
        if (departmentsFilter.value.includes(department.code)) return;
        departmentsFilter.value.push(department.code);
        selectedElements.value.push({
            id: department.code,
            value: `${department.name} (${department.code})`,
            type: TerritoryFilterType.DEPARTMENT,
        });
    }

    function setStationFilter(station: Station) {
        if (stationCodeFilter.value.includes(station.code)) return;
        stationCodeFilter.value.push(station.code);
        selectedElements.value.push({
            id: station.code,
            value: `${station.nom} (${station.departement})`,
            type: TerritoryFilterType.STATION,
        });
    }

    function setRegionFilter(region: { code: string; name: string }) {
        if (regionsFilter.value.includes(region.code)) return;
        regionsFilter.value.push(region.code);
        selectedElements.value.push({
            id: region.code,
            value: region.name,
            type: TerritoryFilterType.REGION,
        });
    }

    function setTerritoryFilter(territory: { code: string; name: string }) {
        if (territoriesFilter.value.includes(territory.code)) return;
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
                    (d) => d !== code,
                );
                break;
            case TerritoryFilterType.STATION:
                stationCodeFilter.value = stationCodeFilter.value.filter(
                    (s) => s !== code,
                );
                break;
            case TerritoryFilterType.REGION:
                regionsFilter.value = regionsFilter.value.filter(
                    (r) => r !== code,
                );
                break;
            case TerritoryFilterType.TERRITORY:
                territoriesFilter.value = territoriesFilter.value.filter(
                    (t) => t !== code,
                );
                break;
        }
    }

    return {
        recordsChartRef,
        pickedDateStart,
        pickedDateEnd,
        granularity,
        sliceTypeSwitchEnabled,
        sliceType,
        sliceDatepickerDate,
        chartTypeSwitchEnabled,
        chartType,
        setGranularity,
        setChartType,
        stationCodeFilter,
        departmentsFilter,
        regionsFilter,
        territoriesFilter,
        selectedElements,
        setDepartmentFilter,
        setStationFilter,
        setRegionFilter,
        setTerritoryFilter,
        removeItemFromFilter,
        recordsData,
        pending,
        error,
    };
});
