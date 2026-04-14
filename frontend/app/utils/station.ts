import type { DeviationStationIdAndName } from "~/types/common";

export const getStationById = (
    stations: DeviationStationIdAndName[],
    stationId: string,
): DeviationStationIdAndName | null => {
    return stations.find((station) => station.station_id === stationId) || null;
};
