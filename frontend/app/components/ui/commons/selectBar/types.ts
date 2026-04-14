import type { ShallowRef } from "vue";
import type {
    TemperatureDeviationGraphResponse,
    NationalIndicatorResponse,
    TemperatureRecordsResponse,
} from "~/types/api";

export type GranularityType = "year" | "month" | "day";

export type SliceType = "full" | "month_of_year" | "day_of_month";

export type ChartType = "line" | "bar" | "scatter" | "pyramid" | "calendar";

export interface SelectBarAdapter<
    T =
        | NationalIndicatorResponse
        | TemperatureDeviationGraphResponse
        | TemperatureRecordsResponse,
> {
    // Date
    granularity: Ref<GranularityType>;
    pickedDateStart: Ref<Date>;
    pickedDateEnd: Ref<Date>;

    // Slice type
    sliceTypeSwitchEnabled?: Ref<boolean>;
    sliceType?: Ref<SliceType>;
    sliceDatepickerDate?: Ref<Date>;

    chartRef?: ShallowRef;
    data: Ref<T | undefined>;

    // Chart type
    chartTypeSwitchEnabled?: Ref<boolean>;
    chartType?: Ref<ChartType>;
<<<<<<< HEAD
    chartTypeOptions?: { label: string; value: ChartType; icon: string }[];
=======
    chartTypes?: { label: string; value: ChartType; icon: string }[];
>>>>>>> 93cda2a (add calendar graph from main branch (#290))

    pending: Ref<boolean>;

    // Territory filters (optional, specific to records)
    selectedElements?: Ref<{ value: string; id: string; type: string }[]>;

    // Methods
    setGranularity: (value: GranularityType) => void;
    setChartType?: (value: ChartType) => void;
    turnOffSliceType?: (value: boolean) => void;

    // Export configuration
    exportConfig: {
        chartName: string;
        csvHeaders: string[];
        getCsvRows: () => unknown[] | undefined;
    };

    features: {
        hasSliceType: boolean;
        hasChartTypeSelector: boolean;
        hasExport: boolean;
    };
}
