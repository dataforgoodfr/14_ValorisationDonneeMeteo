import { refDebounced } from "@vueuse/core";
import type { DeviationTableParams, DeviationTableResponse } from "~/types/api";
import type {
    StringFilterValue,
    RangeFilterValue,
    FilterValue,
} from "~/components/ui/commons/filterBarTypes";
import { departements } from "~/data/records/departements";

type DeviationTableFilters = {
    name?: StringFilterValue;
    departement?: StringFilterValue;
    deviation?: RangeFilterValue;
};

const debounceDuration = 300;

export const useDeviationTableStore = defineStore("deviationTableStore", () => {
    // Pagination
    const page = ref(1);
    const pageSize = ref(10);

    // Filters
    const stationIds = ref<string[]>([]);
    const departments = ref<string[]>([]);
    const deviationMin = ref<string | undefined>(undefined);
    const deviationMax = ref<string | undefined>(undefined);

    // Static options
    const staticOptions = {
        departement: departements.map((d) => ({
            value: d.code,
            label: `${d.code} - ${d.name}`,
        })),
    };

    const filters = computed<DeviationTableFilters>(() => {
        const result: DeviationTableFilters = {};
        if (stationIds.value.length >= 1)
            result.name = { type: "string", values: stationIds.value };
        if (departments.value.length >= 1)
            result.departement = { type: "string", values: departments.value };
        if (deviationMin.value || deviationMax.value)
            result.deviation = {
                type: "number-range",
                min: deviationMin.value,
                max: deviationMax.value,
            };
        return result;
    });

    function setFilter(id: string, value: FilterValue) {
        if (value.type === "string") {
            if (id === "name") stationIds.value = value.values;
            if (id === "departement") departments.value = value.values;
        } else if (value.type === "number-range" && id === "deviation") {
            deviationMin.value = value.min;
            deviationMax.value = value.max;
        }
    }

    function clearFilter(id: string) {
        if (id === "name") stationIds.value = [];
        if (id === "departement") departments.value = [];
        if (id === "deviation") {
            deviationMin.value = undefined;
            deviationMax.value = undefined;
        }
    }

    const debouncedStationIds = refDebounced(stationIds, debounceDuration);
    const debouncedDepartments = refDebounced(departments, debounceDuration);
    const debouncedDevMin = refDebounced(deviationMin, debounceDuration);
    const debouncedDevMax = refDebounced(deviationMax, debounceDuration);

    computed<DeviationTableParams>(() => {
        const result: DeviationTableParams = {
            limit: pageSize.value,
            offset: (page.value - 1) * pageSize.value,
        };
        if (debouncedStationIds.value.length >= 1)
            result.station_ids = debouncedStationIds.value.join(",");
        if (debouncedDepartments.value.length >= 1)
            result.departments = debouncedDepartments.value.join(",");
        if (debouncedDevMin.value)
            result.deviation_min = Number(debouncedDevMin.value);
        if (debouncedDevMax.value)
            result.deviation_max = Number(debouncedDevMax.value);
        return result;
    });

    // Fake data
    const fakeData: DeviationTableResponse = {
        count: 5,
        results: [
            {
                station_id: "07149",
                station_name: "Orly",
                departement: "94",
                deviation: 1.2,
            },
            {
                station_id: "07156",
                station_name: "Paris-Montsouris",
                departement: "75",
                deviation: -0.8,
            },
            {
                station_id: "07181",
                station_name: "Melun",
                departement: "77",
                deviation: 2.1,
            },
            {
                station_id: "07222",
                station_name: "Tours",
                departement: "37",
                deviation: -1.5,
            },
            {
                station_id: "07460",
                station_name: "Marseille-Marignane",
                departement: "13",
                deviation: 3.4,
            },
        ],
    };

    const data = computed<DeviationTableResponse>(() => {
        let results = fakeData.results;

        if (debouncedStationIds.value.length >= 1) {
            results = results.filter((r) =>
                debouncedStationIds.value.includes(r.station_id),
            );
        }

        if (debouncedDepartments.value.length >= 1) {
            results = results.filter((r) =>
                debouncedDepartments.value.includes(r.departement),
            );
        }

        if (debouncedDevMin.value) {
            results = results.filter(
                (r) => r.deviation >= Number(debouncedDevMin.value),
            );
        }

        if (debouncedDevMax.value) {
            results = results.filter(
                (r) => r.deviation <= Number(debouncedDevMax.value),
            );
        }

        const offset = (page.value - 1) * pageSize.value;
        const paginated = results.slice(offset, offset + pageSize.value);

        return { count: results.length, results: paginated };
    });
    const pending = ref(false);
    const error = ref(null);

    // TODO: remplacer par useTemperatureDeviation(params) quand le back est prêt
    // const data = computed(() => fakeData);
    // const pending = ref(false);
    // const error = ref(null);

    return {
        page,
        pageSize,
        filters,
        staticOptions,
        setFilter,
        clearFilter,
        data,
        pending,
        error,
    };
});
