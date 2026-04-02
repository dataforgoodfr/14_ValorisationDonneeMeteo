import { refDebounced } from "@vueuse/core";
import { useTemperatureRecords } from "~/composables/useTemperature";
import { departements } from "~/data/records/departements";
import type {
    RecordKind,
    TypeRecords,
    TemperatureRecordsParams,
} from "~/types/api";

const debounceDuration = 300;

export const useRecordsStore = defineStore("recordsStore", () => {
    // Pagination
    const page = ref(1);
    const pageSize = ref(10);

    // Query shape
    const typeRecords = ref<TypeRecords>("hot");
    const recordKind = ref<RecordKind>("absolute");

    // Filters — stored as strings to stay compatible with FilterBar's range inputs
    const stationIds = ref<string[]>([]);
    const departments = ref<string[]>([]);
    const temperatureMin = ref("");
    const temperatureMax = ref("");
    const dateStart = ref("");
    const dateEnd = ref("");

    // Unique values for the Département dropdown
    const uniqueValues = {
        departement: departements.map((d) => ({
            value: d.code,
            label: `${d.code} - ${d.name}`,
        })),
    };

    // Computed shapes expected by FilterBar (for active chips / initial state)
    const stringFilters = computed(() => {
        const filters: Record<string, string[]> = {};

        if (stationIds.value.length >= 1) {
            filters.name = stationIds.value;
        }
        if (departments.value.length >= 1) {
            filters.departement = departments.value;
        }

        return filters;
    });

    const rangeFilters = computed(() => {
        const filters: Record<string, { min?: string; max?: string }> = {};

        if (temperatureMin.value || temperatureMax.value) {
            filters.record = {
                min: temperatureMin.value,
                max: temperatureMax.value,
            };
        }
        if (dateStart.value || dateEnd.value) {
            filters.record_date = {
                min: dateStart.value,
                max: dateEnd.value,
            };
        }

        return filters;
    });

    // Map FilterBar field IDs to typed store state
    function setStringFilter(id: string, values: string[]) {
        if (id === "name") stationIds.value = values;
        else if (id === "departement") departments.value = values;
    }

    function setRangeFilter(id: string, min: string, max: string) {
        if (id === "record") {
            temperatureMin.value = min;
            temperatureMax.value = max;
        } else if (id === "record_date") {
            dateStart.value = min;
            dateEnd.value = max;
        }
    }

    function clearFilter(id: string) {
        if (id === "name") {
            stationIds.value = [];
        } else if (id === "departement") {
            departments.value = [];
        } else if (id === "record") {
            temperatureMin.value = "";
            temperatureMax.value = "";
        } else if (id === "record_date") {
            dateStart.value = "";
            dateEnd.value = "";
        }
    }

    // Debounce text inputs before sending to the API
    const debouncedStationIds = refDebounced(stationIds, debounceDuration);
    const debouncedDepartments = refDebounced(departments, debounceDuration);
    const debouncedTempMin = refDebounced(temperatureMin, debounceDuration);
    const debouncedTempMax = refDebounced(temperatureMax, debounceDuration);
    const debouncedDateStart = refDebounced(dateStart, debounceDuration);
    const debouncedDateEnd = refDebounced(dateEnd, debounceDuration);

    const params = computed<TemperatureRecordsParams>(() => {
        const result: TemperatureRecordsParams = {
            type_records: typeRecords.value,
            record_kind: recordKind.value,
            limit: pageSize.value,
            offset: (page.value - 1) * pageSize.value,
        };

        if (debouncedStationIds.value.length >= 1) {
            result.station_ids = debouncedStationIds.value;
        }
        if (debouncedDepartments.value.length >= 1) {
            result.departments = debouncedDepartments.value;
        }
        if (debouncedTempMin.value) {
            result.temperature_min = Number(debouncedTempMin.value);
        }
        if (debouncedTempMax.value) {
            result.temperature_max = Number(debouncedTempMax.value);
        }
        if (debouncedDateStart.value) {
            result.date_start = debouncedDateStart.value;
        }
        if (debouncedDateEnd.value) {
            result.date_end = debouncedDateEnd.value;
        }

        return result;
    });

    const { data: recordsData, pending, error } = useTemperatureRecords(params);

    return {
        page,
        pageSize,
        typeRecords,
        recordKind,
        stringFilters,
        rangeFilters,
        uniqueValues,
        setStringFilter,
        setRangeFilter,
        clearFilter,
        recordsData,
        pending,
        error,
    };
});
