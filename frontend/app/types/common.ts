import type { TemperatureDeviationGraphStationSerie } from "./api";

export type DeviationStationIdAndName = Omit<
    TemperatureDeviationGraphStationSerie,
    "data"
>;
