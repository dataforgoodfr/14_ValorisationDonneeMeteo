import { refDebounced } from "@vueuse/core";
import { useTemperatureRecords } from "~/composables/useTemperature.fake";

const DEBOUNCE_DURATION = 300;

const COLUMN_ID_TO_QUERY_PARAM: Record<string, string> = {
    name: "station_name_filter",
    departement: "departement_filter",
};

export const useRecordsStore = defineStore("recordsStore", () => {
    // Record type filter
    const recordType = ref<"Chaud" | "Froid">("Chaud");

    // Date range — default to the past year
    const defaultStartDate = new Date();
    defaultStartDate.setFullYear(defaultStartDate.getFullYear() - 1);
    const startDate = ref(defaultStartDate.toISOString().split("T")[0]);
    const endDate = ref(new Date().toISOString().split("T")[0]);

    // Pagination
    const page = ref(1);
    const pageSize = ref(3);

    // Per-column filter state (TanStack Table format)
    const columnFilters = ref<{ id: string; value: unknown }[]>([]);

    // Debounced values used to drive API calls
    const debouncedStartDate = refDebounced(startDate, DEBOUNCE_DURATION);
    const debouncedEndDate = refDebounced(endDate, DEBOUNCE_DURATION);
    const debouncedColumnFilters = refDebounced(
        columnFilters,
        DEBOUNCE_DURATION,
    );

    // Reset to page 1 whenever any filter changes
    watch(
        [debouncedStartDate, debouncedEndDate, debouncedColumnFilters],
        () => {
            page.value = 1;
        },
    );

    const params = computed(() => ({
        date_start: debouncedStartDate.value || undefined,
        date_end: debouncedEndDate.value || undefined,
        record_type: recordType.value,
        limit: pageSize.value,
        offset: (page.value - 1) * pageSize.value,
        ...Object.fromEntries(
            debouncedColumnFilters.value
                .filter((f) => f.value)
                .map((f) => [COLUMN_ID_TO_QUERY_PARAM[f.id] ?? f.id, f.value]),
        ),
    }));

    const { data: recordsData, pending, error } = useTemperatureRecords(params);

    return {
        recordType,
        startDate,
        endDate,
        page,
        pageSize,
        columnFilters,
        recordsData,
        pending,
        error,
    };
});
