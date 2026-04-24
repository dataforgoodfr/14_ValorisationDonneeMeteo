import type { GraphicComponentOption } from "echarts";
import { COLORS } from "~/constants/colors";

export const ATTRIBUTION_TEXT =
    "Source : Météo-France opensource data\nCrédits : Infoclimat, DataForGood";
export const ATTRIBUTION_FONT_SIZE = 10;

export const CHART_ATTRIBUTION_GRAPHIC: GraphicComponentOption = {
    type: "text",
    right: 10,
    bottom: 0,
    style: {
        text: ATTRIBUTION_TEXT,
        fill: COLORS.foreground,
        fontSize: ATTRIBUTION_FONT_SIZE,
    },
};
