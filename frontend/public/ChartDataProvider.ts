export function GetMockupData(): ChartDataSerie {
    const RetArray: ChartDataSerie = [];
    let CurTemp = 5;
    let CurDate = new Date("2025-01-01");
    let Dt = 0;
    for (let i = 0; i < 365; i++) {
        //CurTemp+=Math.random()*5-2.5
        CurTemp =
            10 * Math.sin(((i - 100) / 180) * 3.141592654) +
            6 +
            Math.random() * 3 -
            1.5;
        const Std = 5 * Math.random();
        Dt =
            Math.sin(((i - 100) / 18) * 3.141592654) * 4 +
            Math.random() * 3 -
            1.5;
        RetArray.push({
            date: CurDate,
            ITN: CurTemp,
            Delta: Dt,
            StdDev: Std,
            Min: CurTemp - Std - Std * Math.random(),
            Max: CurTemp + Std + Std * Math.random(),
        });
        CurDate = new Date(CurDate.getTime() + 24 * 3600 * 1000);
    }
    return RetArray;
}

export enum TimeAxisType {
    Day,
    Month,
    Year,
}

export interface ChartDataPoint {
    date: Date;
    ITN: number;
    Delta: number;
    StdDev: number;
    Min: number;
    Max: number;
}

type ChartDataSerie = ChartDataPoint[];

export function GetChartData(_type: TimeAxisType): ChartDataSerie {
    return GetMockupData();
}
