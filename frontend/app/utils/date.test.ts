import { describe, expect, it } from "vitest";
import {
    dateToStringDMY,
    dateToStringYMD,
    formatDateLongForDisplay,
    fromLocalToUTC,
    fromUTCToLocal,
    getLastAvailableDayOfYear,
    getLastDayOfYear,
    getOneDayBeforeDate,
} from "./date";

describe("Date", () => {
    const firstDayDateToConvert = new Date("Jan 01 2025 00:00:00");
    const lastDayDateToConvert = new Date("Dec 31 2025 00:00:00");

    describe("dateToStringYMD", () => {
        it("should convert to 'YYYY-MM-DD' string", () => {
            const convertedDate = dateToStringYMD(firstDayDateToConvert);
            expect(convertedDate).toBe("2025-01-01");
        });
        it("should convert to 'YYYY-MM-DD' string", () => {
            const convertedDate = dateToStringYMD(lastDayDateToConvert);
            expect(convertedDate).toBe("2025-12-31");
        });
    });
    describe("dateToStringDMY", () => {
        it("should convert to 'DD/MM/YYYY' string", () => {
            const convertedDate = dateToStringDMY(firstDayDateToConvert);
            expect(convertedDate).toBe("01/01/2025");
        });
        it("should convert to 'DD/MM/YYYY' string", () => {
            const convertedDate = dateToStringDMY(lastDayDateToConvert);
            expect(convertedDate).toBe("31/12/2025");
        });
    });

    describe("getOneDayBeforeDate", () => {
        it("should return the date 1 day before", () => {
            const year = new Date("2000-06-15T12:30:45Z");
            expect(getOneDayBeforeDate(year)).toStrictEqual(
                new Date("2000-06-14T00:00:00Z"),
            );
        });
    });

    describe("getLastDayOfYear", () => {
        it("should return the last day of the year", () => {
            const year = new Date("2000-06-15T12:30:45Z");
            expect(getLastDayOfYear(year)).toStrictEqual(
                new Date("2000-12-31T00:00:00Z"),
            );
        });
    });

    describe("getLastAvailableDayOfYear", () => {
        describe("given the current date", () => {
            it("should return the previous day", () => {
                const today = new Date("2026-04-23T11:04:00Z");
                expect(getLastAvailableDayOfYear(today, today)).toStrictEqual(
                    new Date("2026-04-22T00:00:00Z"),
                );
            });
        });

        describe("given a date in a past year", () => {
            it("should return the last day of that year", () => {
                const today = new Date("2026-04-23T11:04:00Z");
                const year = new Date("2000-06-15T12:30:45Z");
                expect(getLastAvailableDayOfYear(year, today)).toStrictEqual(
                    new Date("2000-12-31T00:00:00Z"),
                );
            });
        });
    });

    describe("formatDateLongForDisplay", () => {
        it("should convert to 'D MMMM YYYY' string", () => {
            const convertedDate = formatDateLongForDisplay(
                firstDayDateToConvert,
            );
            expect(convertedDate).toBe("1 janvier 2025");
        });

        it("should convert to 'D MMMM YYYY' string", () => {
            const convertedDate =
                formatDateLongForDisplay(lastDayDateToConvert);
            expect(convertedDate).toBe("31 décembre 2025");
        });
    });

    describe("fromLocalToUTC", () => {
        it("should convert to UTC", () => {
            const localDate = new Date(2000, 6 - 1, 15, 12, 30, 45, 123);
            expect(fromLocalToUTC(localDate)).toStrictEqual(
                new Date("2000-06-15T12:30:45.123Z"),
            );
        });
    });

    describe("fromUTCToLocal", () => {
        it("should convert to local", () => {
            const utcDate = new Date("2000-06-15T12:30:45.123Z");
            expect(fromUTCToLocal(utcDate)).toStrictEqual(
                new Date(2000, 6 - 1, 15, 12, 30, 45, 123),
            );
        });
    });
});
