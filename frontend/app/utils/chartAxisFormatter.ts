import type { GranularityType } from "~/components/ui/commons/selectBar/types";

export function xAxisTimeFormatter(granularity: GranularityType): string {
    return {
        year: "{yyyy}",
        month: "{MMM}-{yyyy}",
        day: "{dd}-{MMM}-{yyyy}",
    }[granularity];
}
