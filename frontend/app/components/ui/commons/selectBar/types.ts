import type { ShallowRef } from "vue";
import type { DeviationResponse, NationalIndicatorResponse } from "~/types/api";

export type GranularityType = "year" | "month" | "day";

export type SliceType = "full" | "month_of_year" | "day_of_month";

export type ChartType = "line" | "bar";

export interface SelectBarAdapter<
    T = NationalIndicatorResponse | DeviationResponse,
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

    pending: Ref<boolean>;

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
