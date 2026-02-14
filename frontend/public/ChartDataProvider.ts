import { writeFile } from "fs/promises";
import fs from "fs";

export const MockedUpDataFileName = "./public/MockedUpData.json";

export function InitMockupData(): void {
    let MockUpFileExists = false;
    try {
        fs.statSync(MockedUpDataFileName);
        MockUpFileExists = true;
    } catch {}
    if (import.meta.server && !MockUpFileExists) {
        console.log("Mocking up data");
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

        // Only once on the server
        //await writeFile();
        fs.writeFileSync(MockedUpDataFileName, JSON.stringify(RetArray));
    }
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

export type ChartDataSerie = ChartDataPoint[];
