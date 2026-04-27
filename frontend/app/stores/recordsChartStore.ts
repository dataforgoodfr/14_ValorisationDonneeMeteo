import { dateToStringYMD } from "~/utils/date";
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

type SelectedItem = {
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

    const selectedElements = ref<SelectedItem[]>([
        {
            id: "FR",
            value: "France Métropolitaine",
            type: TerritoryFilterType.TERRITORY,
        },
    ]);

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

    const params = computed<TemperatureRecordsGraphParams>(() => ({
        date_start: dateToStringYMD(pickedDateStart.value),
        date_end: dateToStringYMD(pickedDateEnd.value),
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

    watch(periodType, (value) => {
        if (value === "season") {
            season.value = "spring";
            month.value = undefined;
        } else if (value === "month") {
            month.value = 1;
            season.value = undefined;
        } else {
            season.value = undefined;
            month.value = undefined;
        }
    });

    const turnOffSliceType = (value: boolean) => {
        if (!value) {
            periodType.value = "all_time";
            month.value = undefined;
            season.value = undefined;
        }
    };

    function setDepartmentFilter(department: { code: string; name: string }) {
        selectedElements.value = [
            {
                id: department.code,
                value: `${department.name} (${department.code})`,
                type: TerritoryFilterType.DEPARTMENT,
            },
        ];
    }

    function setStationFilter(station: Station) {
        if (
            selectedElements.value.some(
                (el) =>
                    el.type === TerritoryFilterType.STATION &&
                    el.id === station.code,
            )
        )
            return;
        selectedElements.value = [
            ...selectedElements.value,
            {
                id: station.code,
                value: `${station.nom} (${station.departement})`,
                type: TerritoryFilterType.STATION,
            },
        ];
    }

    function setRegionFilter(region: { code: string; name: string }) {
        selectedElements.value = [
            {
                id: region.code,
                value: region.name,
                type: TerritoryFilterType.REGION,
            },
        ];
    }

    function setTerritoryFilter(territory: { code: string; name: string }) {
        selectedElements.value = [
            {
                id: territory.code,
                value: territory.name,
                type: TerritoryFilterType.TERRITORY,
            },
        ];
    }

    function removeItemFromFilter(type: TerritoryFilterType, code: string) {
        selectedElements.value = selectedElements.value.filter(
            (element) => !(element.type === type && element.id === code),
        );
        if (selectedElements.value.length === 0) {
            selectedElements.value = [
                {
                    id: "FR",
                    value: "France Métropolitaine",
                    type: TerritoryFilterType.TERRITORY,
                },
            ];
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
        setDepartmentFilter,
        setStationFilter,
        setRegionFilter,
        setTerritoryFilter,
        removeItemFromFilter,
        recordsData,
        processedRecordsData,
        recordKind,
        pending,
        error,
    };
});
