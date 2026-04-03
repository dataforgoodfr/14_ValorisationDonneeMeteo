// ===== Generic pagination wrapper (Django REST LimitOffsetPagination) =====

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

// ===== Station types =====

export interface Station {
    code: string;
    nom: string;
    departement: number;
    poste_ouvert: boolean;
    type_poste: number;
    lon: number;
    lat: number;
    alt: number;
    poste_public: boolean;
}

export interface StationDetail extends Station {
    created_at: string;
    updated_at: string;
}

export interface StationFilters {
    code?: string;
    departement?: number;
    poste_ouvert?: boolean;
    poste_public?: boolean;
    lat_min?: number;
    lat_max?: number;
    lon_min?: number;
    lon_max?: number;
    search?: string;
    ordering?: string;
    limit?: number;
    offset?: number;
}

// ===== National Indicator (ITN) types =====

export interface NationalIndicatorParams {
    date_start: string;
    date_end: string;
    granularity: "year" | "month" | "day";
    slice_type?: "full" | "month_of_year" | "day_of_month";
    month_of_year?: number;
    day_of_month?: number;
}

export interface NationalIndicatorMetadata {
    date_start: string;
    date_end: string;
    baseline: string;
    granularity: "year" | "month" | "day";
    slice_type: "full" | "month_of_year" | "day_of_month";
    month_of_year?: number;
    day_of_month?: number;
}

export interface NationalIndicatorDataPoint {
    date: string;
    temperature: number;
    baseline_mean: number;
    baseline_std_dev_upper: number;
    baseline_std_dev_lower: number;
    baseline_max: number;
    baseline_min: number;
    isInterpolated?: boolean;
}

export interface NationalIndicatorResponse {
    metadata: NationalIndicatorMetadata;
    time_series: NationalIndicatorDataPoint[];
}

// ===== Ecart à la normale (Temperature Deviation) types =====

export interface DeviationParams {
    date_start: string;
    date_end: string;
    granularity: "year" | "month" | "day";
    station_ids?: string;
    include_national: boolean;
}

export interface DeviationMetadata {
    date_start: string;
    date_end: string;
    baseline: string;
    granularity: "year" | "month" | "day";
}

export interface DeviationNational {
    data: DeviationDataPoint[];
}

export interface DeviationStationSerie {
    station_id: string;
    station_name: string;
    data: DeviationDataPoint[];
}

export interface DeviationDataPoint {
    date: string;
    deviation: number;
    temperature: number;
    baseline_mean: number;
}

export interface DeviationResponse {
    metadata: DeviationMetadata;
    national: DeviationNational;
    stations: DeviationStationSerie[];
}

// ===== Temperature Records types =====

export type RecordKind = "historical" | "absolute";
export type RecordScope = "monthly" | "seasonal" | "all_time";
export type TypeRecords = "hot" | "cold" | "all";

export interface TemperatureRecordsParams {
    record_kind?: RecordKind;
    record_scope?: RecordScope;
    type_records?: TypeRecords;
    date_start?: string;
    date_end?: string;
    station_ids?: string;
    departments?: string;
    temperature_min?: number;
    temperature_max?: number;
    limit?: number;
    offset?: number;
}

export interface TemperatureRecordEntry {
    value: number;
    date: string;
}

export interface TemperatureRecordStation {
    id: string;
    name: string;
    hot_records: TemperatureRecordEntry[];
    cold_records: TemperatureRecordEntry[];
}

export interface TemperatureRecordsMetadata {
    date_start: string | null;
    date_end: string | null;
    record_kind: RecordKind;
    record_scope: RecordScope;
    type_records: TypeRecords;
    station_ids: string[];
    departments: string[];
    temperature_min: number | null;
    temperature_max: number | null;
}

export interface TemperatureRecordsResponse {
    count: number;
    metadata: TemperatureRecordsMetadata;
    stations: TemperatureRecordStation[];
}

// ===== API Error type =====

export interface ApiError {
    error: {
        code: string;
        message: string;
        details?: Record<string, unknown>;
    };
}
