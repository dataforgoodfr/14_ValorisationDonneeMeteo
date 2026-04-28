import type { ItnStation } from "../types/api";

export const ITN_STATIONS: ItnStation[] = [
    { code: "47091001", nom: "AGEN-LA GARENNE", lon: 0.594667, lat: 44.172167 },
    { code: "20148001", nom: "BASTIA", lon: 9.485167, lat: 42.540667 },
    { code: "25056001", nom: "BESANCON", lon: 5.988833, lat: 47.249 },
    { code: "14137001", nom: "CAEN-CARPIQUET", lon: -0.456167, lat: 49.18 },
    { code: "36063001", nom: "CHATEAUROUX  DEOLS", lon: 1.741, lat: 46.869833 },
    { code: "63113001", nom: "CLERMONT-FD", lon: 3.149333, lat: 45.786833 },
    { code: "16089001", nom: "COGNAC", lon: -0.315833, lat: 45.665 },
    { code: "21473001", nom: "DIJON-LONGVIC", lon: 5.088333, lat: 47.267833 },
    { code: "72181001", nom: "LE MANS", lon: 0.194167, lat: 47.945833 },
    { code: "59343001", nom: "LILLE-LESQUIN", lon: 3.0975, lat: 50.57 },
    { code: "26198001", nom: "MONTELIMAR", lon: 4.733, lat: 44.581167 },
    { code: "54526001", nom: "NANCY-ESSEY", lon: 6.2215, lat: 48.687833 },
    { code: "44020001", nom: "NANTES-BOUGUENAIS", lon: -1.608833, lat: 47.15 },
    { code: "58160001", nom: "NEVERS-MARZY", lon: 3.1145, lat: 46.999333 },
    { code: "06088001", nom: "NICE", lon: 7.209, lat: 43.648833 },
    { code: "30189001", nom: "NIMES-COURBESSAC", lon: 4.406333, lat: 43.856833 },
    { code: "45055001", nom: "ORLEANS", lon: 1.778167, lat: 47.990667 },
    { code: "75114001", nom: "PARIS-MONTSOURIS", lon: 2.337833, lat: 48.821667 },
    { code: "66136001", nom: "PERPIGNAN", lon: 2.872833, lat: 42.737167 },
    { code: "86027001", nom: "POITIERS-BIARD", lon: 0.314333, lat: 46.593833 },
    { code: "51449002", nom: "REIMS-PRUNAY", lon: 4.155333, lat: 49.209833 },
    { code: "35281001", nom: "RENNES-ST JACQUES", lon: -1.734, lat: 48.068833 },
    { code: "67124001", nom: "STRASBOURG-ENTZHEIM", lon: 7.640333, lat: 48.5495 },
    { code: "31069001", nom: "TOULOUSE-BLAGNAC", lon: 1.378833, lat: 43.621 },
    { code: "33281001", nom: "BORDEAUX-MERIGNAC", lon: -0.691333, lat: 44.830667 },
    { code: "29075001", nom: "BREST-GUIPAVAS", lon: -4.391167, lat: 48.453833 },
    { code: "73054001", nom: "BOURG ST MAURICE", lon: 6.763333, lat: 45.612667 },
    { code: "69029001", nom: "LYON-BRON", lon: 4.949167, lat: 45.721333 },
    { code: "64549001", nom: "PAU-UZEIN", lon: -0.416333, lat: 43.385 },
    { code: "51183001", nom: "REIMS-COURCY", lon: 4.050667, lat: 49.306167 },
    { code: "13054001", nom: "MARIGNANE", lon: 5.216, lat: 43.437667 },
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
