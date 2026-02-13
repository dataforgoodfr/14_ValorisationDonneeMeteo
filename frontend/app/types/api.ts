// ===== Generic pagination wrapper (Django REST LimitOffsetPagination) =====

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

// ===== Station types =====

export interface Station {
    id: number;
    code: string;
    nom: string;
    departement: number;
    frequence: string;
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

// ===== Hourly measurement types =====

export interface HourlyMeasurement {
    id: number;
    station: number;
    station_code: string;
    lat: number;
    lon: number;
    validity_time: string;
    t: number | null;
    td: number | null;
    tx: number | null;
    tn: number | null;
    u: number | null;
    dd: number | null;
    ff: number | null;
    rr1: number | null;
    vv: number | null;
    n: number | null;
    pres: number | null;
    pmer: number | null;
}

export interface HourlyDataFilters {
    station?: number;
    station_code?: string;
    validity_time_after?: string;
    validity_time_before?: string;
    t_min?: number;
    t_max?: number;
    ordering?: string;
    limit?: number;
    offset?: number;
}

// ===== Daily measurement types =====

export interface DailyMeasurement {
    id: number;
    station: number;
    station_code: string;
    nom_usuel: string;
    lat: number;
    lon: number;
    alti: number;
    date: string;
    rr: number | null;
    tn: number | null;
    tx: number | null;
    tm: number | null;
    ffm: number | null;
    fxy: number | null;
}

export interface DailyDataFilters {
    station?: number;
    station_code?: string;
    date_after?: string;
    date_before?: string;
    tn_min?: number;
    tx_max?: number;
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
}

export interface NationalIndicatorResponse {
    metadata: NationalIndicatorMetadata;
    time_series: NationalIndicatorDataPoint[];
}

// ===== API Error type =====

export interface ApiError {
    error: {
        code: string;
        message: string;
        details?: Record<string, unknown>;
    };
}
