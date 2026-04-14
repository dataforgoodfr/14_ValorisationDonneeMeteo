import { refDebounced } from "@vueuse/core";
import { useTemperatureRecords } from "~/composables/useTemperature";
import { departements } from "~/data/records/departements";
import { dateToStringYMD } from "~/utils/date";
import type {
    TypeRecords,
    PeriodType,
    Season,
    TemperatureRecordsParams,
    TemperatureRecordFlatEntry,
} from "~/types/api";
import type {
    StringFilterValue,
    RangeFilterValue,
    DateFilterValue,
    FilterValue,
} from "~/components/ui/commons/filterBarTypes";

type RecordsFilters = {
    name?: StringFilterValue;
    departement?: StringFilterValue;
    record?: RangeFilterValue;
    record_date?: DateFilterValue;
};

const debounceDuration = 300;

export const periodOptions = [
    { value: "all_time", label: "Toute l'année" },
    { value: "season_spring", label: "Printemps" },
    { value: "season_summer", label: "Été" },
    { value: "season_autumn", label: "Automne" },
    { value: "season_winter", label: "Hiver" },
    { value: "month_1", label: "Janvier" },
    { value: "month_2", label: "Février" },
    { value: "month_3", label: "Mars" },
    { value: "month_4", label: "Avril" },
    { value: "month_5", label: "Mai" },
    { value: "month_6", label: "Juin" },
    { value: "month_7", label: "Juillet" },
    { value: "month_8", label: "Août" },
    { value: "month_9", label: "Septembre" },
    { value: "month_10", label: "Octobre" },
    { value: "month_11", label: "Novembre" },
    { value: "month_12", label: "Décembre" },
];

export const useRecordsTableStore = defineStore("recordsTableStore", () => {
    // Pagination
    const page = ref(1);
    const pageSize = ref(10);

    // Query shape
    const typeRecords = ref<TypeRecords>("hot");
    const periodSelection = ref("all_time");

    // Filters
    const stationIds = ref<string[]>([]);
    const departments = ref<string[]>([]);
    const temperatureMin = ref<string | undefined>(undefined);
    const temperatureMax = ref<string | undefined>(undefined);
    const dateStart = ref<Date | undefined>(undefined);
    const dateEnd = ref<Date | undefined>(undefined);

    // Static options for the Département dropdown
    const staticOptions = {
        departement: departements.map((d) => ({
            value: d.code,
            label: `${d.code} - ${d.name}`,
        })),
    };

    const filters = computed<RecordsFilters>(() => {
        const result: RecordsFilters = {};

        if (stationIds.value.length >= 1) {
            result.name = { type: "string", values: stationIds.value };
        }
        if (departments.value.length >= 1) {
            result.departement = { type: "string", values: departments.value };
        }
        if (temperatureMin.value || temperatureMax.value) {
            result.record = {
                type: "number-range",
                min: temperatureMin.value,
                max: temperatureMax.value,
            };
        }
        if (dateStart.value || dateEnd.value) {
            result.record_date = {
                type: "date-range",
                min: dateStart.value,
                max: dateEnd.value,
            };
        }

        return result;
    });

    function setFilter(id: string, value: FilterValue) {
        page.value = 1;
        if (value.type === "string") {
            if (id === "name") {
                stationIds.value = value.values;
            } else if (id === "departement") {
                departments.value = value.values;
            }
        } else if (value.type === "number-range") {
            if (id === "record") {
                temperatureMin.value = value.min;
                temperatureMax.value = value.max;
            }
        } else if (value.type === "date-range") {
            if (id === "record_date") {
                dateStart.value = value.min;
                dateEnd.value = value.max;
            }
        }
    }

    function clearFilter(id: string) {
        page.value = 1;
        if (id === "name") {
            stationIds.value = [];
        } else if (id === "departement") {
            departments.value = [];
        } else if (id === "record") {
            temperatureMin.value = undefined;
            temperatureMax.value = undefined;
        } else if (id === "record_date") {
            dateStart.value = undefined;
            dateEnd.value = undefined;
        }
    }

    // Debounce filter inputs before applying client-side filters
    const debouncedStationIds = refDebounced(stationIds, debounceDuration);
    const debouncedDepartments = refDebounced(departments, debounceDuration);
    const debouncedTempMin = refDebounced(temperatureMin, debounceDuration);
    const debouncedTempMax = refDebounced(temperatureMax, debounceDuration);
    const debouncedDateStart = refDebounced(dateStart, debounceDuration);
    const debouncedDateEnd = refDebounced(dateEnd, debounceDuration);

    // Build API params from periodSelection
    const params = computed<TemperatureRecordsParams>(() => {
        const result: TemperatureRecordsParams = {
            type_records: typeRecords.value,
        };

        if (periodSelection.value.startsWith("season_")) {
            result.period_type = "season" as PeriodType;
            result.season = periodSelection.value.replace(
                "season_",
                "",
            ) as Season;
        } else if (periodSelection.value.startsWith("month_")) {
            result.period_type = "month" as PeriodType;
            result.month = parseInt(
                periodSelection.value.replace("month_", ""),
            );
        }

        return result;
    });

    // Reset page when API params or client-side filters change
    watch(
        [
            params,
            debouncedStationIds,
            debouncedDepartments,
            debouncedTempMin,
            debouncedTempMax,
            debouncedDateStart,
            debouncedDateEnd,
        ],
        () => {
            page.value = 1;
        },
    );

    const { data: rawRecords, pending, error } = useTemperatureRecords(params);

    // Group flat list by station, keeping the last record per station (= absolute record)
    const absoluteRecords = computed<TemperatureRecordFlatEntry[]>(() => {
        const stationMap = new Map<string, TemperatureRecordFlatEntry>();
        for (const record of rawRecords.value ?? []) {
            stationMap.set(record.station_id, record);
        }
        return Array.from(stationMap.values());
    });

    // Apply client-side filters
    const filteredRecords = computed<TemperatureRecordFlatEntry[]>(() => {
        let result = absoluteRecords.value;

        if (debouncedStationIds.value.length > 0) {
            result = result.filter((r) =>
                debouncedStationIds.value.includes(r.station_id),
            );
        }
        if (debouncedDepartments.value.length > 0) {
            result = result.filter((r) =>
                debouncedDepartments.value.includes(r.department),
            );
        }
        if (debouncedTempMin.value) {
            result = result.filter(
                (r) => r.record_value >= Number(debouncedTempMin.value),
            );
        }
        if (debouncedTempMax.value) {
            result = result.filter(
                (r) => r.record_value <= Number(debouncedTempMax.value),
            );
        }
        if (debouncedDateStart.value) {
            const start = dateToStringYMD(debouncedDateStart.value);
            result = result.filter((r) => r.record_date >= start);
        }
        if (debouncedDateEnd.value) {
            const end = dateToStringYMD(debouncedDateEnd.value);
            result = result.filter((r) => r.record_date <= end);
        }

        return result;
    });

    const filteredCount = computed(() => filteredRecords.value.length);

    const pagedStations = computed<TemperatureRecordFlatEntry[]>(() => {
        const start = (page.value - 1) * pageSize.value;
        return filteredRecords.value.slice(start, start + pageSize.value);
    });

    return {
        page,
        pageSize,
        typeRecords,
        periodSelection,
        filters,
        staticOptions,
        setFilter,
        clearFilter,
        pagedStations,
        filteredCount,
        pending,
        error,
    };
});
