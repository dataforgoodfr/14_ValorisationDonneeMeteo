import { h } from "vue";

export const CENTERED_TD = { class: { td: "text-center" } };
export const CENTERED_TH = { class: { th: "text-center" } };
export const CENTERED_COL = { class: { th: "text-center", td: "text-center" } };

export const STATION_META = {
    class: {
        th: "text-center w-44",
        td: "w-44 max-w-44 overflow-hidden",
    },
};

export const REGION_META = {
    class: {
        th: "text-center w-32",
        td: "w-32 max-w-32 overflow-hidden text-center",
    },
};

export function truncatedCell(value: string) {
    return h("span", { class: "block truncate", title: value }, value);
}

export const HOT_BADGE_CLASS =
    "bg-red-200! ring-1! ring-red-450/25! text-red-450!";
export const COLD_BADGE_CLASS =
    "bg-slate-200! ring-1! ring-blue-350/25! text-blue-600!";

export function temperatureBadgeClass(isHot: boolean): string {
    return isHot ? HOT_BADGE_CLASS : COLD_BADGE_CLASS;
}
