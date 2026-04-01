import { refDebounced } from "@vueuse/core";
// TODO: Replace with the real API call when the endpoint is implemented.
import { useTemperatureRecordsFake } from "~/composables/useTemperature.fake";
import type { Station } from "~/types/api";

const debounceDuration = 300;

type SelectedItem = {
    item: Station | { code: string; name: string };
    value: string;
    type: "STATION" | "DEPARTMENT";
};

export const useRecordsGraphStore = defineStore("recordsGraphStore", () => {
    // Date range — default to the past year
    const defaultStartDate = new Date();
    defaultStartDate.setFullYear(defaultStartDate.getFullYear() - 1);
    const startDate = ref<Date>(defaultStartDate);
    const endDate = ref<Date>(new Date());
    const departmentsFilter = ref<string[]>([]);
    const stationNameFilter = ref<string[]>([]);
    const selectedElements = ref<SelectedItem[]>([]);

    // Pagination
    const page = ref(1);
    const pageSize = ref(3);

    // Debounced values used to drive API calls
    const debouncedStartDate = refDebounced(startDate, debounceDuration);
    const debouncedEndDate = refDebounced(endDate, debounceDuration);
    const debouncedDepartmentsFilter = refDebounced(
        departmentsFilter,
        debounceDuration,
    );
    const debouncedStationNameFilter = refDebounced(
        stationNameFilter,
        debounceDuration,
    );

    const params = computed(() => ({
        date_start: debouncedStartDate.value.toISOString().split("T")[0],
        date_end: debouncedEndDate.value.toISOString().split("T")[0],
        limit: pageSize.value,
        offset: (page.value - 1) * pageSize.value,
        departement_filter: debouncedDepartmentsFilter.value.join(","),
        station_name_filter: debouncedStationNameFilter.value.join(","),
    }));

    function setDepartmentFilter(department: { code: string; name: string }) {
        if (departmentsFilter.value.includes(department.code)) {
            return;
        }
        departmentsFilter.value.push(department.code);
        selectedElements.value.push({
            item: department,
            value: `${department.name} (${department.code})`,
            type: "DEPARTMENT",
        });
    }

    function removeDepartmentFilter(department: {
        code: string;
        name: string;
    }) {
        departmentsFilter.value = departmentsFilter.value.filter(
            (d) => d !== department.code,
        );
        selectedElements.value = selectedElements.value.filter(
            (e) =>
                !(
                    e.type === "DEPARTMENT" &&
                    e.value === `${department.name} (${department.code})`
                ),
        );
    }

    function setStationFilter(station: Station) {
        if (stationNameFilter.value.includes(station.code)) {
            return;
        }
        stationNameFilter.value.push(station.code);
        selectedElements.value.push({
            item: station,
            value: `${station.nom} (${station.departement})`,
            type: "STATION",
        });
    }

    function removeStationFilter(station: Station) {
        stationNameFilter.value = stationNameFilter.value.filter(
            (s) => s !== station.code,
        );
        selectedElements.value = selectedElements.value.filter(
            (e) =>
                !(
                    e.type === "STATION" &&
                    e.value === `${station.nom} (${station.departement})`
                ),
        );
    }

    const {
        data: recordsData,
        pending,
        error,
    } = useTemperatureRecordsFake(params);

    return {
        startDate,
        endDate,
        setDepartmentFilter,
        removeDepartmentFilter,
        setStationFilter,
        removeStationFilter,
        page,
        pageSize,
        recordsData,
        stationNameFilter,
        departmentsFilter,
        pending,
        error,
        selectedElements,
    };
});
