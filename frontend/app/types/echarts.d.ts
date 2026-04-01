import "echarts/types/dist/shared";
import "echarts/types/dist/echarts";

declare module "echarts/types/dist/shared" {
    interface CallbackDataParams {
        axisId?: string;
        axisIndex?: number;
        axisType?: string;
        axisValue?: string | number;
        axisValueLabel?: string;
    }
}

declare module "echarts/types/dist/echarts" {
    interface DefaultLabelFormatterCallbackParams {
        axisId?: string;
        axisIndex?: number;
        axisType?: string;
        axisValue?: string | number;
        axisValueLabel?: string;
    }
}
