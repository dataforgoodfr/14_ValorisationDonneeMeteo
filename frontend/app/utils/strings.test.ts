import { describe, test, expect } from "vitest";
import { escapeCsvValue, normalizeString } from "./string";

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

describe("escapeCsvValue", () => {
    test("valeur simple — pas de modification", () => {
        expect(escapeCsvValue("Paris")).toBe("Paris");
    });
    test("valeur avec virgule — encapsulée entre guillemets", () => {
        expect(escapeCsvValue("Paris, Lyon")).toBe('"Paris, Lyon"');
    });
    test("valeur avec guillemet — guillemet doublé et encapsulé", () => {
        expect(escapeCsvValue('say "hello"')).toBe('"say ""hello"""');
    });
    test("nombre — converti en string", () => {
        expect(escapeCsvValue(42)).toBe("42");
    });
    test("undefined — chaîne vide", () => {
        expect(escapeCsvValue(undefined)).toBe("");
    });
});
