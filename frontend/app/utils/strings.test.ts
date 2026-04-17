import { describe, test, expect } from "vitest";
import { normalizeString } from "./string";

describe("string", () => {
    test("is normalized", () => {
        const stringToNormalize = normalizeString("Île-de-France");
        expect(stringToNormalize).toBe("Ile-de-France");
    });
    test("is normalized", () => {
        const stringToNormalize = normalizeString("Pyrénées-Atlantiques");
        expect(stringToNormalize).toBe("Pyrenees-Atlantiques");
    });
    test("is normalized", () => {
        const stringToNormalize = normalizeString("Deux-Sèvres");
        expect(stringToNormalize).toBe("Deux-Sevres");
    });
    test("is normalized", () => {
        const stringToNormalize = normalizeString("Côte-d'Or");
        expect(stringToNormalize).toBe("Cote-d'Or");
    });
    test("is NOT normalized", () => {
        const stringToNormalize = normalizeString("Martinique");
        expect(stringToNormalize).toBe("Martinique");
    });
});
