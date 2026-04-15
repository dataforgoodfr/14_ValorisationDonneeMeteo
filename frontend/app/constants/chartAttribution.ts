import type { GraphicComponentOption } from "echarts";

export const CHART_ATTRIBUTION_GRAPHIC: GraphicComponentOption = {
    type: "text",
    right: 10,
    bottom: 0,
    style: {
        text: "Source : Météo-France opensource data\nCrédit : InfoClimat, DataForGood",
        fill: "#3e3e3e",
        fontSize: 10,
    },
};
