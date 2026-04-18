import { refDebounced } from "@vueuse/core";
import type { TemperatureDeviationParams } from "~/types/api";
import type {
    FilterValue,
    RangeFilterValue,
    StringFilterValue,
} from "~/components/ui/commons/filterBarTypes";
import { departements } from "~/data/records/departements";
import { regions } from "~/data/records/regions";

type DeviationTableFilters = {
    name?: StringFilterValue;
    departement?: StringFilterValue;
    region?: StringFilterValue;
    // altitude?: RangeFilterValue;
    deviation?: RangeFilterValue;
    temperatureMean?: RangeFilterValue;
};

const dates = useCustomDate();
const debounceDuration = 300;

export const useDeviationTableStore = defineStore("deviationTableStore", () => {
    // Pagination
    const page = ref(1);
    const pageSize = ref(10);

    // Filters
    const stationIds = ref<string[]>([]);
    const departmentsFilter = ref<string[]>([]);
    const regionsFilter = ref<string[]>([]);
    // const altitudeMin = ref<string | undefined>(undefined);
    // const altitudeMax = ref<string | undefined>(undefined);
    const deviationMin = ref<string | undefined>(undefined);
    const deviationMax = ref<string | undefined>(undefined);
    const temperatureMeanMin = ref<string | undefined>(undefined);
    const temperatureMeanMax = ref<string | undefined>(undefined);

    // Static options
    const staticOptions = {
        departement: departements.map((d) => ({
            value: d.code,
            label: `${d.code} - ${d.name}`,
        })),
        region: regions.map((d) => ({
            value: d.name,
            label: `${d.name}`,
        })),
    };

    const filters = computed<DeviationTableFilters>(() => {
        const result: DeviationTableFilters = {};
        if (stationIds.value.length >= 1)
            result.name = { type: "string", values: stationIds.value };
        if (departmentsFilter.value.length >= 1)
            result.departement = {
                type: "string",
                values: departmentsFilter.value,
            };
        if (regionsFilter.value.length >= 1)
            result.region = { type: "string", values: regionsFilter.value };
        // if (altitudeMin.value || altitudeMax.value)
        //     result.altitude = {
        //         type: "number-range",
        //         min: altitudeMin.value,
        //         max: altitudeMax.value,
        //     };
        if (deviationMin.value || deviationMax.value)
            result.deviation = {
                type: "number-range",
                min: deviationMin.value,
                max: deviationMax.value,
            };
        if (temperatureMeanMin.value || temperatureMeanMax.value)
            result.temperatureMean = {
                type: "number-range",
                min: temperatureMeanMin.value,
                max: temperatureMeanMax.value,
            };
        return result;
    });

    function setFilter(id: string, value: FilterValue) {
        if (value.type === "string") {
            if (id === "name") stationIds.value = value.values;
            if (id === "departement") departmentsFilter.value = value.values;
            if (id === "region") regionsFilter.value = value.values;
        } else if (value.type === "number-range") {
            // if (id === "altitude") {
            //     altitudeMin.value = value.min;
            //     altitudeMax.value = value.max;
            if (id === "deviation") {
                deviationMin.value = value.min;
                deviationMax.value = value.max;
            } else if (id === "temperatureMean") {
                temperatureMeanMin.value = value.min;
                temperatureMeanMax.value = value.max;
            }
        }
    }

    function clearFilter(id: string) {
        if (id === "name") {
            stationIds.value = [];
        } else if (id === "departement") {
            departmentsFilter.value = [];
        } else if (id === "region") {
            regionsFilter.value = [];
            // } else if (id === "altitude") {
            //     altitudeMin.value = undefined;
            //     altitudeMax.value = undefined;
        } else if (id === "deviation") {
            deviationMin.value = undefined;
            deviationMax.value = undefined;
        } else if (id === "temperatureMean") {
            temperatureMeanMin.value = undefined;
            temperatureMeanMax.value = undefined;
        }
    }

    const debouncedStationIds = refDebounced(stationIds, debounceDuration);
    const debouncedDepartments = refDebounced(
        departmentsFilter,
        debounceDuration,
    );
    const debouncedRegions = refDebounced(regionsFilter, debounceDuration);
    // const debouncedAltMin = refDebounced(altitudeMin, debounceDuration);
    // const debouncedAltMax = refDebounced(altitudeMax, debounceDuration);
    const debouncedDevMin = refDebounced(deviationMin, debounceDuration);
    const debouncedDevMax = refDebounced(deviationMax, debounceDuration);
    const debouncedTMeanMin = refDebounced(
        temperatureMeanMin,
        debounceDuration,
    );
    const debouncedTMeanMax = refDebounced(
        temperatureMeanMax,
        debounceDuration,
    );

    const dateStart = ref(dates.lastMonth.value);
    const dateEnd = ref(dates.today.value);
    const ordering = ref<string>("-deviation");

    const params = computed<TemperatureDeviationParams>(() => {
        const result: TemperatureDeviationParams = {
            date_start: dateToStringYMD(dateStart.value),
            date_end: dateToStringYMD(dateEnd.value),
            limit: pageSize.value,
            offset: (page.value - 1) * pageSize.value,
            ordering: ordering.value,
        };
        if (debouncedStationIds.value.length >= 1)
            result.station_ids = debouncedStationIds.value.join(",");
        if (debouncedDepartments.value.length >= 1)
            result.departments = debouncedDepartments.value.join(",");
        if (debouncedRegions.value.length >= 1)
            result.regions = debouncedRegions.value.join(",");
        // if (debouncedAltMin.value)
        //     result.altitude_min = Number(debouncedAltMin.value);
        // if (debouncedAltMax.value)
        //     result.altitude_max = Number(debouncedAltMax.value);
        if (debouncedDevMin.value)
            result.deviation_min = Number(debouncedDevMin.value);
        if (debouncedDevMax.value)
            result.deviation_max = Number(debouncedDevMax.value);
        if (debouncedTMeanMin.value)
            result.temperature_mean_min = Number(debouncedTMeanMin.value);
        if (debouncedTMeanMax.value)
            result.temperature_mean_max = Number(debouncedTMeanMax.value);
        return result;
    });

    function setOrdering(field: string) {
        if (ordering.value === field) {
            ordering.value = `-${field}`;
        } else if (ordering.value === `-${field}`) {
            ordering.value = field;
        } else {
            ordering.value = `-${field}`;
        }
    }

    const {
        data: deviationData,
        pending,
        error,
    } = useTemperatureDeviation(params, undefined, false);

    const exportParams = computed<TemperatureDeviationParams>(() => {
        const { limit: _limit, offset: _offset, ...rest } = params.value;
        return rest;
    });

    return {
        page,
        pageSize,
        filters,
        staticOptions,
        setFilter,
        clearFilter,
        deviationData,
        exportParams,
        pending,
        error,
        dateStart,
        dateEnd,
        ordering,
        setOrdering,
    };
});
