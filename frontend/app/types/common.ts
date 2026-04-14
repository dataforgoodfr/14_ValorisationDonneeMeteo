<<<<<<< HEAD
import type { TemperatureDeviationGraphStationSerie } from "./api";

export type DeviationStationIdAndName = Omit<
    TemperatureDeviationGraphStationSerie,
    "data"
>;
=======
import type { DeviationStationSerie } from "./api";

export type DeviationStationIdAndName = Omit<DeviationStationSerie, "data">;
>>>>>>> 93cda2a (add calendar graph from main branch (#290))
