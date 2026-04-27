export interface ItnStation {
    station_code: string;
    name: string;
    departement: number;
    lon: number;
    lat: number;
    alt: number;
}

export const ITN_STATIONS: ItnStation[] = [
    { station_code: "47091001", name: "AGEN-LA GARENNE", departement: 47, lon: 0.594667, lat: 44.172167, alt: 58 },
    { station_code: "20148001", name: "BASTIA", departement: 20, lon: 9.485167, lat: 42.540667, alt: 10 },
    { station_code: "25056001", name: "BESANCON", departement: 25, lon: 5.988833, lat: 47.249, alt: 307 },
    { station_code: "14137001", name: "CAEN-CARPIQUET", departement: 14, lon: -0.456167, lat: 49.18, alt: 67 },
    { station_code: "36063001", name: "CHATEAUROUX  DEOLS", departement: 36, lon: 1.741, lat: 46.869833, alt: 158 },
    { station_code: "63113001", name: "CLERMONT-FD", departement: 63, lon: 3.149333, lat: 45.786833, alt: 331 },
    { station_code: "16089001", name: "COGNAC", departement: 16, lon: -0.315833, lat: 45.665, alt: 30 },
    { station_code: "21473001", name: "DIJON-LONGVIC", departement: 21, lon: 5.088333, lat: 47.267833, alt: 219 },
    { station_code: "72181001", name: "LE MANS", departement: 72, lon: 0.194167, lat: 47.945833, alt: 51 },
    { station_code: "59343001", name: "LILLE-LESQUIN", departement: 59, lon: 3.0975, lat: 50.57, alt: 47 },
    { station_code: "26198001", name: "MONTELIMAR", departement: 26, lon: 4.733, lat: 44.581167, alt: 73 },
    { station_code: "54526001", name: "NANCY-ESSEY", departement: 54, lon: 6.2215, lat: 48.687833, alt: 212 },
    { station_code: "44020001", name: "NANTES-BOUGUENAIS", departement: 44, lon: -1.608833, lat: 47.15, alt: 26 },
    { station_code: "58160001", name: "NEVERS-MARZY", departement: 58, lon: 3.1145, lat: 46.999333, alt: 175 },
    { station_code: "06088001", name: "NICE", departement: 6, lon: 7.209, lat: 43.648833, alt: 2 },
    { station_code: "30189001", name: "NIMES-COURBESSAC", departement: 30, lon: 4.406333, lat: 43.856833, alt: 59 },
    { station_code: "45055001", name: "ORLEANS", departement: 45, lon: 1.778167, lat: 47.990667, alt: 123 },
    { station_code: "75114001", name: "PARIS-MONTSOURIS", departement: 75, lon: 2.337833, lat: 48.821667, alt: 75 },
    { station_code: "66136001", name: "PERPIGNAN", departement: 66, lon: 2.872833, lat: 42.737167, alt: 42 },
    { station_code: "86027001", name: "POITIERS-BIARD", departement: 86, lon: 0.314333, lat: 46.593833, alt: 125 },
    { station_code: "51449002", name: "REIMS-PRUNAY", departement: 51, lon: 4.155333, lat: 49.209833, alt: 95 },
    { station_code: "35281001", name: "RENNES-ST JACQUES", departement: 35, lon: -1.734, lat: 48.068833, alt: 36 },
    { station_code: "67124001", name: "STRASBOURG-ENTZHEIM", departement: 67, lon: 7.640333, lat: 48.5495, alt: 150 },
    { station_code: "31069001", name: "TOULOUSE-BLAGNAC", departement: 31, lon: 1.378833, lat: 43.621, alt: 151 },
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
