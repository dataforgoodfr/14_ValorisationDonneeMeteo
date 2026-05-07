import {
    dateToStringYMD,
    getFirstDayOfMonth,
    getFirstDayOfYearInLocal,
    getLastAvailableDayOfMonth,
    getLastAvailableDayOfYearInLocal,
} from "~/utils/date";
import type {
    PeriodType,
    Season,
    Station,
    TemperatureRecordsGraphParams,
    TemperatureRecordsGraphRecord,
    TemperatureRecordsGraphResponse,
    TypeRecords,
} from "~/types/api";
import { useCustomDate } from "#imports";
import type {
    GranularityType,
    ChartType,
} from "~/components/ui/commons/selectBar/types";

const dates = useCustomDate();

export enum TerritoryFilterType {
    STATION = "STATION",
    DEPARTMENT = "DEPARTMENT",
    REGION = "REGION",
    TERRITORY = "TERRITORY",
}

export type SelectedItem = {
    value: string;
    id: string;
    type: TerritoryFilterType;
};

export const useRecordsChartStore = defineStore("recordChartStore", () => {
    const recordsChartRef = shallowRef();

    const pickedDateStart = ref(dates.absoluteMinDataDate.value);
    const pickedDateEnd = ref(dates.today.value);
    const maxDate = ref(dates.today.value);

    const granularity: Ref<GranularityType> = ref<GranularityType>("year");
    const chartType: Ref<ChartType> = ref<ChartType>("pyramid");

    const typeRecords: Ref<TypeRecords> = ref("all");
    const sliceTypeSwitchEnabled = ref(false);
    const periodType: Ref<PeriodType> = ref("all_time");
    const month = ref<number | undefined>(undefined);
    const season = ref<Season | undefined>(undefined);
    const initialElement: SelectedItem = {
        id: "FR",
        value: "France Métropolitaine",
        type: TerritoryFilterType.TERRITORY,
    };

    const selectedElements = ref<SelectedItem[]>([initialElement]);

    const stationCodeFilter = computed(() =>
        selectedElements.value
            .filter((el) => el.type === TerritoryFilterType.STATION)
            .map((el) => el.id),
    );

    const departmentsFilter = computed(() =>
        selectedElements.value
            .filter((el) => el.type === TerritoryFilterType.DEPARTMENT)
            .map((el) => el.id),
    );

    const regionsFilter = computed(() =>
        selectedElements.value
            .filter((el) => el.type === TerritoryFilterType.REGION)
            .map((el) => el.id),
    );

    const territoriesFilter = computed(() =>
        selectedElements.value
            .filter((el) => el.type === TerritoryFilterType.TERRITORY)
            .map((el) => el.id),
    );

    const territoire = computed(() => {
        const els = selectedElements.value;
        if (els.length !== 1) return "france";
        const only = els[0]!;
        if (only.type === TerritoryFilterType.TERRITORY) return "france";
        if (only.type === TerritoryFilterType.STATION) return "station";
        if (only.type === TerritoryFilterType.DEPARTMENT) return "department";
        return "region";
    });

    const territoireId = computed<string | undefined>(() => {
        const els = selectedElements.value;
        if (els.length !== 1) return undefined;
        const only = els[0]!;
        if (only.type === TerritoryFilterType.TERRITORY) return undefined;
        return only.id;
    });

    const effectiveDateStart = computed(() => {
        if (granularity.value === "year")
            return getFirstDayOfYearInLocal(pickedDateStart.value);
        if (granularity.value === "month")
            return getFirstDayOfMonth(pickedDateStart.value);
        return pickedDateStart.value;
    });

    const effectiveDateEnd = computed(() => {
        if (granularity.value === "year")
            return getLastAvailableDayOfYearInLocal(pickedDateEnd.value);
        if (granularity.value === "month")
            return getLastAvailableDayOfMonth(pickedDateEnd.value);
        return pickedDateEnd.value;
    });

    const params = computed<TemperatureRecordsGraphParams>(() => ({
        date_start: dateToStringYMD(effectiveDateStart.value),
        date_end: dateToStringYMD(effectiveDateEnd.value),
        granularity: granularity.value,
        type_records: typeRecords.value,
        period_type: periodType.value,
        month: periodType.value === "month" ? month.value : undefined,
        season: periodType.value === "season" ? season.value : undefined,
        territoire: territoire.value,
        territoire_id: territoireId.value,
    }));

    const {
        data: recordsData,
        pending,
        error,
    } = useTemperatureRecordsGraph(params);

    const recordKind = ref<"absolute" | "historical">("absolute");

    const processedRecordsData = computed<
        TemperatureRecordsGraphResponse | undefined
    >(() => {
        if (!recordsData.value) return undefined;
        if (recordKind.value === "historical") return recordsData.value;

        const latestByKey = new Map<string, TemperatureRecordsGraphRecord>();
        for (const record of recordsData.value.records) {
            const key = `${record.station_id}__${record.type_records}`;
            const existing = latestByKey.get(key);
            if (!existing || record.date > existing.date) {
                latestByKey.set(key, record);
            }
        }
        return {
            buckets: recordsData.value.buckets,
            records: Array.from(latestByKey.values()),
        };
    });

    const setGranularity = (value: GranularityType) => {
        granularity.value = value;
        pickedDateEnd.value = dates.today.value;
        maxDate.value = dates.today.value;
        if (value === "day") {
            sliceTypeSwitchEnabled.value = false;
            pickedDateStart.value = dates.lastYear.value;
        }
        if (value === "month") {
            pickedDateStart.value = dates.last10Year.value;
        }
        if (value === "year") {
            pickedDateStart.value = dates.absoluteMinDataDate.value;
        }
    };

    const setChartType = (value: ChartType) => {
        chartType.value = value;
    };

    watch(periodType, () => {
        season.value = undefined;
        month.value = undefined;
    });

    const turnOffSliceType = (value: boolean) => {
        if (!value) {
            periodType.value = "all_time";
            month.value = undefined;
            season.value = undefined;
        }
    };

    function addFilter(
        type: TerritoryFilterType,
        id: string,
        value: string,
    ): void {
        const isElementAlreadySelected = selectedElements.value.some(
            (el) => el.type === type && el.id === id,
        );
        if (!isElementAlreadySelected) {
            selectedElements.value = [
                ...selectedElements.value,
                {
                    id,
                    value,
                    type,
                },
            ];
        }
    }

    function addDepartmentFilter(department: {
        code: string;
        name: string;
    }): void {
        const value = `${department.name} (${department.code})`;

        addFilter(TerritoryFilterType.DEPARTMENT, department.code, value);
    }

    function addStationFilter(station: Station): void {
        const id = station.code;
        const value = `${station.nom} (${station.departement})`;

        addFilter(TerritoryFilterType.STATION, id, value);
    }

    function addRegionFilter(region: { code: string; name: string }): void {
        addFilter(TerritoryFilterType.REGION, region.code, region.name);
    }

    function addTerritoryFilter(territory: {
        code: string;
        name: string;
    }): void {
        addFilter(
            TerritoryFilterType.TERRITORY,
            territory.code,
            territory.name,
        );
    }

    function removeItemFromFilter(type: TerritoryFilterType, code: string) {
        selectedElements.value = selectedElements.value.filter(
            (element) => !(element.type === type && element.id === code),
        );
        if (selectedElements.value.length === 0) {
            selectedElements.value = [initialElement];
        }
    }

    return {
        recordsChartRef,
        pickedDateStart,
        pickedDateEnd,
        maxDate,
        granularity,
        chartType,
        typeRecords,
        sliceTypeSwitchEnabled,
        periodType,
        month,
        season,
        selectedElements,
        stationCodeFilter,
        departmentsFilter,
        regionsFilter,
        territoriesFilter,
        setGranularity,
        setChartType,
        turnOffSliceType,
        addDepartmentFilter,
        addStationFilter,
        addRegionFilter,
        addTerritoryFilter,
        removeItemFromFilter,
        recordsData,
        processedRecordsData,
        recordKind,
        pending,
        error,
    };
});
