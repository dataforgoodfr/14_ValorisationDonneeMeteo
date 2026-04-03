export type FilterType =
    | "string"
    | "string-async"
    | "date-range"
    | "number-range";

export interface FilterField {
    id: string;
    label: string;
    type: FilterType;
}

export interface FilterOption {
    value: string;
    label: string;
}

export type StringFilterValue = { type: "string"; values: string[] };
export type RangeFilterValue = {
    type: "number-range";
    min?: string;
    max?: string;
};
export type DateFilterValue = { type: "date-range"; min?: Date; max?: Date };
export type FilterValue =
    | StringFilterValue
    | RangeFilterValue
    | DateFilterValue;
