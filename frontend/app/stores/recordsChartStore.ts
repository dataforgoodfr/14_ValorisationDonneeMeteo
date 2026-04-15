import { refDebounced } from "@vueuse/core";
import { dateToStringYMD } from "~/utils/date";
import type { Station, TemperatureRecordsParams } from "~/types/api";
import { useCustomDate } from "#imports";
import type {
    GranularityType,
    SliceType,
    ChartType,
} from "~/components/ui/commons/selectBar/types";

const debounceDuration = 300;
const dates = useCustomDate();

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

    // Date range
    const pickedDateStart = ref(new Date(1950, 0, 1));
    const pickedDateEnd = ref(dates.twoDaysAgo.value);
    const debouncedStartDate = refDebounced(pickedDateStart, debounceDuration);
    const debouncedEndDate = refDebounced(pickedDateEnd, debounceDuration);

    // Chart controls
    const granularity: Ref<GranularityType> = ref<GranularityType>("year");
    const sliceTypeSwitchEnabled = ref(false);
    const sliceType: Ref<SliceType> = ref<SliceType>("full");
    const sliceDatepickerDate = ref(new Date(2006, 0, 1));
    const chartTypeSwitchEnabled = ref(false);
    const chartType: Ref<ChartType> = ref<ChartType>("pyramid");

    // Record filters
    const recordKind: Ref<"historical" | "absolute"> = ref("absolute");
    const recordScope: Ref<"monthly" | "seasonal" | "all_time"> =
        ref("all_time");
    const typeRecords: Ref<"hot" | "cold" | "all"> = ref("all");
    const temperatureMin = ref<number | null>(null);
    const temperatureMax = ref<number | null>(null);

    // Territory filters
    const stationCodeFilter = ref<string[]>([]);
    const departmentsFilter = ref<string[]>([]);
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

    const debouncedDepartmentsFilter = refDebounced(
        departmentsFilter,
        debounceDuration,
    );
    const debouncedStationCodeFilter = refDebounced(
        stationCodeFilter,
        debounceDuration,
    );

    const params = computed<TemperatureRecordsParams>(() => ({
        date_start: dateToStringYMD(debouncedStartDate.value),
        date_end: dateToStringYMD(debouncedEndDate.value),
        limit: pageSize.value,
        offset: (page.value - 1) * pageSize.value,
        departement_filter: debouncedDepartmentsFilter.value.join(","),
        station_name_filter: debouncedStationCodeFilter.value.join(","),

        record_kind: recordKind.value,
        record_scope: recordScope.value,
        type_records: typeRecords.value,
        ...(debouncedStationCodeFilter.value.length > 0
            ? { station_ids: debouncedStationCodeFilter.value.join(",") }
            : {}),
        ...(debouncedDepartmentsFilter.value.length > 0
            ? { departments: debouncedDepartmentsFilter.value.join(",") }
            : {}),
        temperature_min: temperatureMin.value ?? undefined,
        temperature_max: temperatureMax.value ?? undefined,
    }));

    const setGranularity = (value: GranularityType) => {
        sliceType.value = "full";
        granularity.value = value;
        if (value === "day") {
            sliceTypeSwitchEnabled.value = false;
        }
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
    // TODO: Replace with useTemperatureRecords(params) when backend is ready
    // const { data: recordsData, pending, error } = useTemperatureRecords(params);
    const {
        data: recordsData,
        pending,
        error,
    } = useTemperatureRecordsChartFake(params);

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
        page,
        pageSize,
        recordKind,
        recordScope,
        typeRecords,
        temperatureMin,
        temperatureMax,
        recordsData,
        pending,
        error,
    };
});
