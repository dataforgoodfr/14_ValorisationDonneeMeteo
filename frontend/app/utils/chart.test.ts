import { describe, expect, test } from "vitest";
import { getXAxisIndexes } from "./chart";

describe("chart", () => {
    describe("getXAxisIndexes", () => {
        test.each([
            { count: 1, result: [0] },
            { count: 2, result: [0, 1] },
            { count: 3, result: [0, 1, 2] },
            { count: 5, result: [0, 1, 2, 3, 4] },
        ])("should return $result for $count axes", ({ count, result }) => {
            expect(getXAxisIndexes(count)).toEqual(result);
        });
    });
});
