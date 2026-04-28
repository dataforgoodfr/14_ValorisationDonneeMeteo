import {
    HOT_BADGE_CLASS,
    COLD_BADGE_CLASS,
    HOT_BORDER_CLASS,
    COLD_BORDER_CLASS,
} from "~/constants/tableUtils";

export function useTemperatureTypeStyle(type: MaybeRef<"hot" | "cold">) {
    const isHot = computed(() => toValue(type) === "hot");

    const badgeClass = computed(() =>
        isHot.value ? HOT_BADGE_CLASS : COLD_BADGE_CLASS,
    );

    const borderClass = computed(() =>
        isHot.value ? HOT_BORDER_CLASS : COLD_BORDER_CLASS,
    );

    const icon = computed(() =>
        isHot.value ? "i-lucide-sun" : "i-lucide-snowflake",
    );

    const label = computed(() => (isHot.value ? "CHAUD" : "FROID"));

    return { isHot, badgeClass, borderClass, icon, label };
}
