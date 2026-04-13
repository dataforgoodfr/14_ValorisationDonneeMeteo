import type { DeviationStationIdAndName } from "~/types/common";

export const getStationById = (
    stations: DeviationStationIdAndName[],
    station_id: string,
): DeviationStationIdAndName | null => {
    return (
        stations.find((station) => station.station_id === station_id) || null
    );
};
