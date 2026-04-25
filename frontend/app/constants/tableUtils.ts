import { h, type Ref } from "vue";
import { UButton } from "#components";
import type { TableColumn } from "@nuxt/ui";

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

export const TABLE_HEADER_BTN_CLASS =
    "-mx-2.5 font-semibold text-highlighted w-full justify-center text-base";

export const TABLE_HEADER_BTN_MULTILINE_CLASS =
    "-mx-2.5 font-semibold text-highlighted w-full justify-center whitespace-normal leading-tight text-center text-base";

export const EXPORT_BTN_UI = {
    base: "bg-slate-450 ring-1 ring-blue-350 text-white",
};

export const TEMPERATURE_BADGE_SIZE = "lg";

export const HOT_BADGE_CLASS =
    "bg-rose-200 ring-1 ring-red-450/25 text-rose-600";
export const COLD_BADGE_CLASS =
    "bg-slate-200 ring-1 ring-blue-350/25 text-blue-650 dark:text-blue-700";

export function truncatedCell(value: string) {
    return h("span", { class: "block truncate", title: value }, value);
}

export function temperatureBadgeClass(isHot: boolean): string {
    return isHot ? HOT_BADGE_CLASS : COLD_BADGE_CLASS;
}

export function makeSortableColFactory<T>(
    ordering: Ref<string>,
    setOrdering: (key: string) => void,
) {
    return function (
        key: string,
        label: string,
        options: {
            sortKey?: string;
            meta?: TableColumn<T>["meta"];
            headerCustom?: TableColumn<T>["header"];
            cellCustom?: TableColumn<T>["cell"];
        } = {},
    ): TableColumn<T> {
        const sortKey = options.sortKey ?? key;
        return {
            accessorKey: key,
            header: options.headerCustom
                ? options.headerCustom
                : () =>
                      h(UButton, {
                          variant: "ghost",
                          label,
                          title: label,
                          trailingIcon: ordering.value.includes(sortKey)
                              ? ordering.value.startsWith("-")
                                  ? "i-lucide-arrow-down"
                                  : "i-lucide-arrow-up"
                              : "i-lucide-arrow-up-down",
                          color: "neutral",
                          class: TABLE_HEADER_BTN_CLASS,
                          onClick: () => setOrdering(sortKey),
                      }),
            cell: options.cellCustom ? options.cellCustom : undefined,
            ...(options.meta ? { meta: options.meta } : {}),
        };
    };
}
