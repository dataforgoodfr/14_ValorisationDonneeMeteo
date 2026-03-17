import { refDebounced } from "@vueuse/core";
// TODO: Replace with the real API call when the endpoint is implemented.
import { useTemperatureRecordsFake } from "~/composables/useTemperature.fake";

const debounceDuration = 300;

const columnIdToQueryParam: Record<string, string> = {
    name: "station_name_filter",
    departement: "departement_filter",
};

export const useRecordsStore = defineStore("recordsStore", () => {
    // Record type filter
    const recordType = ref<"Chaud" | "Froid">("Chaud");

    // Date range — default to the past year
    const defaultStartDate = new Date();
    defaultStartDate.setFullYear(defaultStartDate.getFullYear() - 1);
    const startDate = ref<Date>(defaultStartDate);
    const endDate = ref<Date>(new Date());

    // Pagination
    const page = ref(1);
    const pageSize = ref(3);

    // Per-column filter state (TanStack Table format)
    const columnFilters = ref<{ id: string; value: unknown }[]>([]);

    function getFilter(id: string): string {
        return (
            (columnFilters.value.find((f) => f.id === id)?.value as string) ??
            ""
        );
    }

    function setFilter(id: string, value: string) {
        columnFilters.value = [
            ...columnFilters.value.filter((f) => f.id !== id),
            ...(value ? [{ id, value }] : []),
        ];
    }

    // Debounced values used to drive API calls
    const debouncedStartDate = refDebounced(startDate, debounceDuration);
    const debouncedEndDate = refDebounced(endDate, debounceDuration);
    const debouncedColumnFilters = refDebounced(
        columnFilters,
        debounceDuration,
    );

    // Reset to page 1 whenever any filter changes
    watch(
        [debouncedStartDate, debouncedEndDate, debouncedColumnFilters],
        () => {
            page.value = 1;
        },
    );

    const params = computed(() => ({
        date_start: debouncedStartDate.value.toISOString().split("T")[0],
        date_end: debouncedEndDate.value.toISOString().split("T")[0],
        record_type: recordType.value,
        limit: pageSize.value,
        offset: (page.value - 1) * pageSize.value,
        ...Object.fromEntries(
            debouncedColumnFilters.value
                .filter((f) => f.value)
                .map((f) => [columnIdToQueryParam[f.id] ?? f.id, f.value]),
        ),
    }));

    const {
        data: recordsData,
        pending,
        error,
    } = useTemperatureRecordsFake(params);

    return {
        recordType,
        startDate,
        endDate,
        page,
        pageSize,
        columnFilters,
        getFilter,
        setFilter,
        recordsData,
        pending,
        error,
    };
});
