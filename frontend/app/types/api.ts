// ===== Generic pagination wrapper (Django REST LimitOffsetPagination) =====

import type {
    GranularityType,
    SliceType,
} from "~/components/ui/commons/selectBar/types";

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

export type StationDetail = Station;

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
    granularity: GranularityType;
    slice_type?: SliceType;
    month_of_year?: number;
    day_of_month?: number;
}

export interface NationalIndicatorMetadata {
    date_start: string;
    date_end: string;
    baseline: string;
    granularity: GranularityType;
    slice_type: SliceType;
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

export interface NationalIndicatorKpiParams {
    date_start: string;
    date_end: string;
}

export interface KpiPeriodStats {
    hot_peak_count: number;
    cold_peak_count: number;
    days_above_baseline: number;
    days_below_baseline: number;
    itn_mean: number | null;
    deviation_from_normal: number | null;
}

export interface NationalIndicatorKpiResponse extends KpiPeriodStats {
    previous: KpiPeriodStats;
}

// ===== Écart à la normale (Temperature Deviation) types =====

export interface TemperatureDeviationParams {
    date_start: string;
    date_end: string;
    station_ids?: string;
    station_search?: string;
    departments?: string;
    regions?: string;
    temperature_mean_min?: number;
    temperature_mean_max?: number;
    deviation_min?: number;
    deviation_max?: number;
    altitude_min?: number;
    altitude_max?: number;
    ordering?: string;
    limit?: number;
    offset?: number;
}

export interface TemperatureDeviationMetadata {
    date_start: string | null;
    date_end: string | null;
    baseline: string;
    filters: {
        station_search: string | null;
        station_ids: string[] | null;
        temperature_mean_min: number | null;
        temperature_mean_max: number | null;
        deviation_min: number | null;
        deviation_max: number | null;
    };
    ordering: string;
}

export interface TemperatureDeviationNational {
    deviation_mean: number;
}

export interface TemperatureDeviationPagination {
    total_count: number;
    limit: number;
    offset: number;
}

export interface TemperatureDeviationStation {
    station_id: string;
    station_name: string;
    temperature_mean: number;
    baseline_mean: number;
    deviation: number;
    alt: number;
    lat: number;
    lon: number;
    department: string;
    region: string;
}

export interface TemperatureDeviationResponse {
    metadata: TemperatureDeviationMetadata;
    national: TemperatureDeviationNational;
    pagination: TemperatureDeviationPagination;
    stations: TemperatureDeviationStation[];
}
export interface DeviationMapParams {
    date_start: string;
    date_end: string;
    limit?: number;
    offset?: number;
    station_ids?: string;
    departments?: string;
    regions?: string;
    ordering?: string;
}

export interface DeviationMapNational {
    deviation_mean: number;
}

export interface DeviationMapStation {
    station_id: string;
    station_name: string;
    temperature_mean: number;
    baseline_mean: number;
    deviation: number;
    lat: number;
    lon: number;
    department: string | null;
    alt: number;
    region: string | null;
}

export interface DeviationMapMetadata {
    date_start: string;
    date_end: string;
    baseline: string;
    filters: Record<string, unknown>;
    ordering: string;
}

export interface DeviationMapPagination {
    total_count: number;
    limit: number;
    offset: number;
}

export interface DeviationMapResponse {
    metadata: DeviationMapMetadata;
    national: DeviationMapNational;
    pagination: DeviationMapPagination;
    stations: DeviationMapStation[];
}

export interface TemperatureDeviationGraphParams {
    date_start: string;
    date_end: string;
    granularity: GranularityType;
    station_ids?: string;
    departments?: string;
    include_national: boolean;
    deviation_min?: number;
    deviation_max?: number;
    limit?: number;
    offset?: number;
    slice_type?: SliceType;
    month_of_year?: number;
    day_of_month?: number;
}

export interface TemperatureDeviationGraphMetadata {
    date_start: string;
    date_end: string;
    baseline: string;
    granularity: GranularityType;
}

export interface TemperatureDeviationGraphNational {
    data: TemperatureDeviationGraphDataPoint[];
}

export interface TemperatureDeviationGraphStationSerie {
    station_id: string;
    station_name: string;
    departement: string;
    data: TemperatureDeviationGraphDataPoint[];
}

export interface TemperatureDeviationGraphDataPoint {
    date: string;
    deviation: number;
    temperature: number;
    baseline_mean: number;
}

export interface TemperatureDeviationGraphResponse {
    count: number;
    metadata: TemperatureDeviationGraphMetadata;
    national: TemperatureDeviationGraphNational;
    stations: TemperatureDeviationGraphStationSerie[];
}

// ===== Temperature Records types =====

export type RecordKind = "historical" | "absolute";
export type RecordScope = "monthly" | "seasonal" | "all_time";
export type TypeRecords = "hot" | "cold" | "all";
export type PeriodType = "all_time" | "season" | "month";
export type Season = "spring" | "summer" | "autumn" | "winter";

export interface TemperatureRecordsParams {
    record_kind?: RecordKind;
    record_scope?: RecordScope;
    type_records?: TypeRecords;
    period_type?: PeriodType;
    season?: Season;
    month?: number;
    date_start?: string;
    date_end?: string;
    station_ids?: string;
    departments?: string;
    temperature_min?: number;
    temperature_max?: number;
    limit?: number;
    offset?: number;
}

export interface TemperatureRecordFlatEntry {
    station_id: string;
    station_name: string;
    department: string;
    record_value: number;
    record_date: string;
    lat: number;
    lon: number;
    alt: number;
}

export interface TemperatureRecordStation {
    id: string;
    name: string;
    departement: number;
    hot_records: TemperatureRecordFlatEntry[];
    cold_records: TemperatureRecordFlatEntry[];
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

// ===== Map shared types =====

export interface MappableStation {
    lat: number;
    lon: number;
    station_name: string;
    value: number;
    record_date?: string;
    department?: string;
}

export interface MapColorConfig {
    min: number;
    max: number;
    stops: [number, string][];
}

export type MapTooltipFormatter = (properties: {
    station_name: string;
    value: number;
    record_date: string | null;
    department: string | null;
}) => string;
// ===== Temperature Records Graph types =====

export interface TemperatureRecordsGraphParams {
    date_start: string;
    date_end: string;
    granularity: "day" | "month" | "year";
    type_records?: TypeRecords;
    period_type?: PeriodType;
    month?: number;
    season?: Season;
    territoire?: "france" | "region" | "department" | "station";
    territoire_id?: string;
}

export interface TemperatureRecordsGraphBucket {
    bucket: string;
    nb_records_battus: number;
}

export interface TemperatureRecordsGraphRecord {
    date: string;
    station_id: string;
    station_name: string;
    type_records: "hot" | "cold";
    valeur: number;
}

export interface TemperatureRecordsGraphResponse {
    buckets: TemperatureRecordsGraphBucket[];
    records: TemperatureRecordsGraphRecord[];
}

// ===== API Error type =====

export interface ApiError {
    error: {
        code: string;
        message: string;
        details?: Record<string, unknown>;
    };
}
