import { describe, test, expect } from "vitest";
import {
    dateToStringDMY,
    dateToStringYMD,
    setToLastDayOfYear,
    formatDateLongForDisplay,
} from "./date";

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

    test("returns the day of today minus 2 days", () => {
        const convertedDate = setToLastDayOfYear(new Date());
        const today = new Date();
        const lastDay = new Date();
        lastDay.setDate(today.getDate() - 2);
        lastDay.setHours(23, 59, 59, 999);
        expect(convertedDate).toStrictEqual(lastDay);
    });

    test("returns last day of the year", () => {
        const dateToConvert = new Date("Jan 01 2024 00:00:00");
        const convertedDate = setToLastDayOfYear(dateToConvert);
        const expectedDate = new Date();
        expectedDate.setFullYear(dateToConvert.getFullYear());
        expectedDate.setMonth(11);
        expectedDate.setDate(31);
        expectedDate.setHours(23, 59, 59, 999);
        expect(convertedDate).toStrictEqual(expectedDate);
    });

    test("is converted to 'DD MMMM YYYY' string", () => {
        const convertedDate = formatDateLongForDisplay(firstDayDateToConvert);
        expect(convertedDate).toBe("1 janvier 2025");
    });

    test("is converted to 'DD MMMM YYYY' string", () => {
        const convertedDate = formatDateLongForDisplay(lastDayDateToConvert);
        expect(convertedDate).toBe("31 décembre 2025");
    });
});
