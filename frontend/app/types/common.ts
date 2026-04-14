import type { DeviationStationSerie } from "./api";

export type DeviationStationIdAndName = Omit<DeviationStationSerie, "data">;
