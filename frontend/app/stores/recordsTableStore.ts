import { refDebounced } from "@vueuse/core";
import { MONTH_LONG } from "~/constants/months";
import { useTemperatureAbsoluteRecords } from "~/composables/useTemperature";
import { departements } from "~/data/records/departements";
import { dateToStringYMD } from "~/utils/date";
import { expandClasseRange } from "~/utils/classeFilter";
import type {
    PeriodType,
    Season,
    TemperatureRecordFlatEntry,
    TemperatureRecordsParams,
    TypeRecords,
} from "~/types/api";
import type {
    DateFilterValue,
    FilterValue,
    RangeFilterValue,
    StringFilterValue,
} from "~/components/ui/commons/filterBarTypes";

type RecordsFilters = {
    name?: StringFilterValue;
    departement?: StringFilterValue;
    record?: RangeFilterValue;
    record_date?: DateFilterValue;
    classe?: StringFilterValue;
    date_de_creation?: RangeFilterValue;
    altitude?: RangeFilterValue;
};

export const periodOptions = [
    { value: "all_time", label: "Toute l'année" },
    { value: "season_spring", label: "Printemps" },
    { value: "season_summer", label: "Été" },
    { value: "season_autumn", label: "Automne" },
    { value: "season_winter", label: "Hiver" },
    ...MONTH_LONG.map((label, i) => ({ value: `month_${i + 1}`, label })),
];

const debounceDuration = 300;

export function computeAbsoluteRecords(
    rawRecords: TemperatureRecordFlatEntry[],
    typeRecords: TypeRecords,
): TemperatureRecordFlatEntry[] {
    const stationMap = new Map<string, TemperatureRecordFlatEntry>();
    for (const record of rawRecords) {
        const currentRecord = stationMap.get(record.station_id)?.record_value;
        if (
            currentRecord === undefined ||
            (typeRecords === "hot" && record.record_value > currentRecord) ||
            (typeRecords === "cold" && record.record_value < currentRecord)
        ) {
            stationMap.set(record.station_id, record);
        }
    }
    return Array.from(stationMap.values());
}

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
    const ordering = ref("");
    const classeFilter = ref<string[]>([]);
    const creationYearMin = ref<string | undefined>(undefined);
    const creationYearMax = ref<string | undefined>(undefined);
    const altMin = ref<string | undefined>(undefined);
    const altMax = ref<string | undefined>(undefined);

    const debouncedStationIds = refDebounced(stationIds, debounceDuration);
    const debouncedDepartments = refDebounced(departments, debounceDuration);
    const debouncedTemperatureMin = refDebounced(
        temperatureMin,
        debounceDuration,
    );
    const debouncedTemperatureMax = refDebounced(
        temperatureMax,
        debounceDuration,
    );
    const debouncedDateStart = refDebounced(dateStart, debounceDuration);
    const debouncedDateEnd = refDebounced(dateEnd, debounceDuration);
    const debouncedClasseFilter = refDebounced(classeFilter, debounceDuration);
    const debouncedCreationYearMin = refDebounced(
        creationYearMin,
        debounceDuration,
    );
    const debouncedCreationYearMax = refDebounced(
        creationYearMax,
        debounceDuration,
    );
    const debouncedAltMin = refDebounced(altMin, debounceDuration);
    const debouncedAltMax = refDebounced(altMax, debounceDuration);

    // Static options for the Département dropdown
    const staticOptions = {
        departement: departements.map((d) => ({
            value: d.code,
            label: `${d.code} - ${d.name}`,
        })),
        classe: ["1", "2", "3"].map((v) => ({ value: v, label: v })),
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
        if (classeFilter.value.length >= 1) {
            result.classe = { type: "string", values: classeFilter.value };
        }
        if (creationYearMin.value || creationYearMax.value) {
            result.date_de_creation = {
                type: "number-range",
                min: creationYearMin.value,
                max: creationYearMax.value,
            };
        }
        if (altMin.value || altMax.value) {
            result.altitude = {
                type: "number-range",
                min: altMin.value,
                max: altMax.value,
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
            } else if (id === "classe") {
                classeFilter.value = expandClasseRange(value.values);
            }
        } else if (value.type === "number-range") {
            if (id === "record") {
                temperatureMin.value = value.min;
                temperatureMax.value = value.max;
            } else if (id === "date_de_creation") {
                creationYearMin.value = value.min;
                creationYearMax.value = value.max;
            } else if (id === "altitude") {
                altMin.value = value.min;
                altMax.value = value.max;
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
        } else if (id === "classe") {
            classeFilter.value = [];
        } else if (id === "date_de_creation") {
            creationYearMin.value = undefined;
            creationYearMax.value = undefined;
        } else if (id === "altitude") {
            altMin.value = undefined;
            altMax.value = undefined;
        }
    }

    function resetFilters() {
        page.value = 1;
        stationIds.value = [];
        departments.value = [];
        temperatureMin.value = undefined;
        temperatureMax.value = undefined;
        dateStart.value = undefined;
        dateEnd.value = undefined;
        classeFilter.value = [];
        creationYearMin.value = undefined;
        creationYearMax.value = undefined;
        altMin.value = undefined;
        altMax.value = undefined;
    }

    const hasActiveFilters = computed(
        () => Object.keys(filters.value).length > 0,
    );

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
            debouncedTemperatureMin,
            debouncedTemperatureMax,
            debouncedDateStart,
            debouncedDateEnd,
            debouncedClasseFilter,
            debouncedCreationYearMin,
            debouncedCreationYearMax,
            debouncedAltMin,
            debouncedAltMax,
        ],
        () => {
            page.value = 1;
        },
    );

    const {
        data: rawRecords,
        pending,
        error,
    } = useTemperatureAbsoluteRecords(
        computed(() => ({ ...params.value, page_size: 9999 })),
    );

    const absoluteRecords = computed<TemperatureRecordFlatEntry[]>(
        () => rawRecords.value?.results ?? [],
    );

    // Apply client-side filters (debounced to avoid filtering on every keystroke)
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
        if (debouncedTemperatureMin.value) {
            result = result.filter(
                (r) => r.record_value >= Number(debouncedTemperatureMin.value),
            );
        }
        if (debouncedTemperatureMax.value) {
            result = result.filter(
                (r) => r.record_value <= Number(debouncedTemperatureMax.value),
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
        if (debouncedClasseFilter.value.length > 0) {
            result = result.filter((r) =>
                debouncedClasseFilter.value.includes(String(r.classe_recente)),
            );
        }
        if (debouncedCreationYearMin.value) {
            const min = Number(debouncedCreationYearMin.value);
            result = result.filter(
                (r) => new Date(r.date_de_creation).getFullYear() >= min,
            );
        }
        if (debouncedCreationYearMax.value) {
            const max = Number(debouncedCreationYearMax.value);
            result = result.filter(
                (r) => new Date(r.date_de_creation).getFullYear() <= max,
            );
        }
        if (debouncedAltMin.value) {
            const min = Number(debouncedAltMin.value);
            result = result.filter((r) => r.alt >= min);
        }
        if (debouncedAltMax.value) {
            const max = Number(debouncedAltMax.value);
            result = result.filter((r) => r.alt <= max);
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
        absoluteRecords,
        pagedStations,
        filteredRecords,
        filteredCount,
        pending,
        error,
        dateStart,
        dateEnd,
        ordering,
        resetFilters,
        hasActiveFilters,
    };
});
