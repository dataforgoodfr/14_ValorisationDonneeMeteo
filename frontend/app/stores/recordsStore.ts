import { refDebounced } from "@vueuse/core";
// TODO: Replace with the real API call when the endpoint is implemented.
import { useTemperatureRecordsFake } from "~/composables/useTemperature.fake";
import { stationNames } from "~/data/records/stationNames";
import { villes } from "~/data/records/villes";
import { departements } from "~/data/records/departements";

const debounceDuration = 300;

export const useRecordsStore = defineStore("recordsStore", () => {
    // Record type filter
    const recordType = ref<"Chaud" | "Froid">("Chaud");

    // Pagination
    const page = ref(1);
    const pageSize = ref(10);

    // String multi-select filters: fieldId -> selected values
    const stringFilters = ref<Record<string, string[]>>({});

    // Range filters: fieldId -> { min, max }
    const rangeFilters = ref<Record<string, { min: string; max: string }>>({});

    // Unique values for filter dropdowns — { value } is sent to the API, { label } is shown in the UI
    const uniqueValues = {
        name: stationNames.map((v) => ({ value: v, label: v })),
        ville: villes.map((v) => ({ value: v, label: v })),
        departement: departements.map((d) => ({
            value: d.code,
            label: `${d.code} - ${d.name}`,
        })),
    };

    function setStringFilter(id: string, values: string[]) {
        if (values.length === 0) {
            const { [id]: _, ...rest } = stringFilters.value;
            stringFilters.value = rest;
        } else {
            stringFilters.value = { ...stringFilters.value, [id]: values };
        }
        page.value = 1;
    }

    function setRangeFilter(id: string, min: string, max: string) {
        if (!min && !max) {
            const { [id]: _, ...rest } = rangeFilters.value;
            rangeFilters.value = rest;
        } else {
            rangeFilters.value = { ...rangeFilters.value, [id]: { min, max } };
        }
        page.value = 1;
    }

    function clearFilter(id: string) {
        const { [id]: _s, ...strRest } = stringFilters.value;
        stringFilters.value = strRest;

        const { [id]: _r, ...rngRest } = rangeFilters.value;
        rangeFilters.value = rngRest;

        page.value = 1;
    }

    // Debounced values used to drive API calls
    const debouncedStringFilters = refDebounced(
        stringFilters,
        debounceDuration,
    );
    const debouncedRangeFilters = refDebounced(rangeFilters, debounceDuration);

    // Reset to page 1 when record type changes (string/range setters handle it themselves)
    watch(recordType, () => {
        page.value = 1;
    });

    const params = computed(() => ({
        record_type: recordType.value,
        limit: pageSize.value,
        offset: (page.value - 1) * pageSize.value,
        string_filters: debouncedStringFilters.value,
        range_filters: debouncedRangeFilters.value,
    }));

    const {
        data: recordsData,
        pending,
        error,
    } = useTemperatureRecordsFake(params);

    return {
        recordType,
        page,
        pageSize,
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
