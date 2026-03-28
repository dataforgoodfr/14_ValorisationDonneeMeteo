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
