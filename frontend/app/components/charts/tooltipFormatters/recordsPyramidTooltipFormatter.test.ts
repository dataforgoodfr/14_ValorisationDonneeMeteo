import { describe, expect, it } from "vitest";
import type {
    DefaultLabelFormatterCallbackParams,
    TooltipComponentFormatterCallbackParams,
} from "echarts";
import { recordsPyramidTooltipFormatter } from "./recordsPyramidTooltipFormatter";

const makeParam = (
    axisValue: string,
    value: { period: string; hot: number; cold: number },
): DefaultLabelFormatterCallbackParams => ({
    componentType: "series",
    componentSubType: "bar",
    componentIndex: 0,
    axisIndex: 0,
    seriesName: "Records",
    name: "",
    dataIndex: 0,
    data: value,
    value,
    axisValue,
    marker: `<span style="color:red;">●</span>`,
    $vars: ["seriesName", "name", "value"],
});

describe("recordsPyramidTooltipFormatter", () => {
    describe("Guard cases", () => {
        it("returns empty string when params is not an array", () => {
            const result = recordsPyramidTooltipFormatter(
                makeParam("", {
                    period: "",
                    hot: 0,
                    cold: 0,
                }),
            );

            expect(result).toBe("");
        });

        it("returns empty string when params array is empty", () => {
            const result = recordsPyramidTooltipFormatter([]);

            expect(result).toBe("");
        });
    });

    describe("Whole returned string", () => {
        it("returns the right string for a period", () => {
            const params: TooltipComponentFormatterCallbackParams = [
                makeParam("Mars", {
                    period: "03",
                    hot: 7,
                    cold: 3,
                }),
            ];

            const result = recordsPyramidTooltipFormatter(params);

            expect(result).toBe(
                "<b>Mars</b><br/>" +
                    '<span style="color:#d32F2F">● Records de chaleur : 7</span><br/>' +
                    '<span style="color:#1976D2">● Records de froid : 3</span><br/>' +
                    '<span style="color:#aaa">Total : 10</span>',
            );
        });
    });
});
