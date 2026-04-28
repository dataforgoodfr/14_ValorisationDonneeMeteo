import * as echarts from "echarts/core";

const TEXT = "#fff";
export const ECHART_DARK_THEME = "dataclimat-dark";

const axisText = { axisLabel: { color: TEXT }, nameTextStyle: { color: TEXT } };

echarts.registerTheme(ECHART_DARK_THEME, {
    textStyle: { color: TEXT },
    title: { textStyle: { color: TEXT }, subtextStyle: { color: TEXT } },
    legend: { textStyle: { color: TEXT } },
    categoryAxis: axisText,
    valueAxis: axisText,
    timeAxis: axisText,
    logAxis: axisText,
});
