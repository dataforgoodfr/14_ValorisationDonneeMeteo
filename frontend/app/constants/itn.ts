export interface ItnStation {
    station_code: string;
    name: string;
    lon: number;
    lat: number;
}

export const ITN_STATIONS: ItnStation[] = [
    { station_code: "47091001", name: "AGEN-LA GARENNE", lon: 0.594667, lat: 44.172167 },
    { station_code: "20148001", name: "BASTIA", lon: 9.485167, lat: 42.540667 },
    { station_code: "25056001", name: "BESANCON", lon: 5.988833, lat: 47.249 },
    { station_code: "14137001", name: "CAEN-CARPIQUET", lon: -0.456167, lat: 49.18 },
    { station_code: "36063001", name: "CHATEAUROUX  DEOLS", lon: 1.741, lat: 46.869833 },
    { station_code: "63113001", name: "CLERMONT-FD", lon: 3.149333, lat: 45.786833 },
    { station_code: "16089001", name: "COGNAC", lon: -0.315833, lat: 45.665 },
    { station_code: "21473001", name: "DIJON-LONGVIC", lon: 5.088333, lat: 47.267833 },
    { station_code: "72181001", name: "LE MANS", lon: 0.194167, lat: 47.945833 },
    { station_code: "59343001", name: "LILLE-LESQUIN", lon: 3.0975, lat: 50.57 },
    { station_code: "26198001", name: "MONTELIMAR", lon: 4.733, lat: 44.581167 },
    { station_code: "54526001", name: "NANCY-ESSEY", lon: 6.2215, lat: 48.687833 },
    { station_code: "44020001", name: "NANTES-BOUGUENAIS", lon: -1.608833, lat: 47.15 },
    { station_code: "58160001", name: "NEVERS-MARZY", lon: 3.1145, lat: 46.999333 },
    { station_code: "06088001", name: "NICE", lon: 7.209, lat: 43.648833 },
    { station_code: "30189001", name: "NIMES-COURBESSAC", lon: 4.406333, lat: 43.856833 },
    { station_code: "45055001", name: "ORLEANS", lon: 1.778167, lat: 47.990667 },
    { station_code: "75114001", name: "PARIS-MONTSOURIS", lon: 2.337833, lat: 48.821667 },
    { station_code: "66136001", name: "PERPIGNAN", lon: 2.872833, lat: 42.737167 },
    { station_code: "86027001", name: "POITIERS-BIARD", lon: 0.314333, lat: 46.593833 },
    { station_code: "51449002", name: "REIMS-PRUNAY", lon: 4.155333, lat: 49.209833 },
    { station_code: "35281001", name: "RENNES-ST JACQUES", lon: -1.734, lat: 48.068833 },
    { station_code: "67124001", name: "STRASBOURG-ENTZHEIM", lon: 7.640333, lat: 48.5495 },
    { station_code: "31069001", name: "TOULOUSE-BLAGNAC", lon: 1.378833, lat: 43.621 },
    { station_code: "33281001", name: "BORDEAUX-MERIGNAC", lon: -0.691333, lat: 44.830667 },
    { station_code: "29075001", name: "BREST-GUIPAVAS", lon: -4.391167, lat: 48.453833 },
    { station_code: "73054001", name: "BOURG ST MAURICE", lon: 6.763333, lat: 45.612667 },
    { station_code: "69029001", name: "LYON-BRON", lon: 4.949167, lat: 45.721333 },
    { station_code: "64549001", name: "PAU-UZEIN", lon: -0.416333, lat: 43.385 },
    { station_code: "51183001", name: "REIMS-COURCY", lon: 4.050667, lat: 49.306167 },
    { station_code: "13054001", name: "MARIGNANE", lon: 5.216, lat: 43.437667 },
];

export const ITN_STATION_WEIGHT = "P1";

export const ITN_SERIES = {
    temperature: "ITN",
    baseline: "ITN des normales",
    extremes: "Extrêmes",
    stdDev: "Écart-type",
};

export const ITN_COLORS = {
    EXTREMES: "rgba(100, 100, 100, 0.2)",
    ECART_TYPE: "rgba(175, 175, 175, 1)",
};
