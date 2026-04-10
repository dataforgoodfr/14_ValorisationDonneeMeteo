import { refDebounced } from "@vueuse/core";
import { useTemperatureRecords } from "~/composables/useTemperature";
import { departements } from "~/data/records/departements";
import { dateToStringYMD } from "~/utils/date";
import type {
    RecordKind,
    TypeRecords,
    TemperatureRecordsParams,
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
    const recordKind = ref<RecordKind>("absolute");

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
            result.station_ids = debouncedStationIds.value.join(",");
        }
        if (debouncedDepartments.value.length >= 1) {
            result.departments = debouncedDepartments.value.join(",");
        }
        if (debouncedTempMin.value) {
            result.temperature_min = Number(debouncedTempMin.value);
        }
        if (debouncedTempMax.value) {
            result.temperature_max = Number(debouncedTempMax.value);
        }
        if (debouncedDateStart.value) {
            result.date_start = dateToStringYMD(debouncedDateStart.value);
        }
        if (debouncedDateEnd.value) {
            result.date_end = dateToStringYMD(debouncedDateEnd.value);
        }

        return result;
    });

    const { data: recordsData, pending, error } = useTemperatureRecords(params);

    return {
        page,
        pageSize,
        typeRecords,
        recordKind,
        filters,
        staticOptions,
        setFilter,
        clearFilter,
        recordsData,
        pending,
        error,
    };
});
