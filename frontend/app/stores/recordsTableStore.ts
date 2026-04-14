import { refDebounced } from "@vueuse/core";
import { useTemperatureRecords } from "~/composables/useTemperature";
import { departements } from "~/data/records/departements";
import { dateToStringYMD } from "~/utils/date";
import type {
    TypeRecords,
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

export const useRecordsTableStore = defineStore("recordsTableStore", () => {
    // Pagination
    const page = ref(1);
    const pageSize = ref(10);

    // Query shape
    const typeRecords = ref<TypeRecords>("hot");

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

    // The API only supports type_records — all other filtering is client-side
    const params = computed<TemperatureRecordsParams>(() => ({
        type_records: typeRecords.value,
    }));

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
