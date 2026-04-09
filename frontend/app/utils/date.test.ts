import { describe, test, expect } from "vitest";
import { dateToStringDMY, dateToStringYMD } from "./date";

describe("Date", () => {
    const firstDayDateToConvert = new Date("Jan 01 2025 00:00:00");
    const lastDayDateToConvert = new Date("Dec 31 2025 00:00:00");

    test("is converted to 'YYYY-MM-DD' string", () => {
        const convertedDate = dateToStringYMD(firstDayDateToConvert);
        expect(convertedDate).toBe("2025-01-01");
    });
    test("is converted to 'YYYY-MM-DD' string", () => {
        const convertedDate = dateToStringYMD(lastDayDateToConvert);
        expect(convertedDate).toBe("2025-12-31");
    });
    test("is converted to 'DD/MM/YYYY' string", () => {
        const convertedDate = dateToStringDMY(firstDayDateToConvert);
        expect(convertedDate).toBe("01/01/2025");
    });

    test("is converted to 'DD/MM/YYYY' string", () => {
        const convertedDate = dateToStringDMY(lastDayDateToConvert);
        expect(convertedDate).toBe("31/12/2025");
    });
});
