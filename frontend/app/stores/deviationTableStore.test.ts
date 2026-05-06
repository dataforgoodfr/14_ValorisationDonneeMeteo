import { describe, test, expect } from "vitest";
import { expandClasseRange } from "../utils/classeFilter";

describe("expandClasseRange", () => {
    test("tableau vide — retourne tableau vide", () => {
        expect(expandClasseRange([])).toEqual([]);
    });

    test("valeur unique — retourne cette valeur", () => {
        expect(expandClasseRange(["2"])).toEqual(["2"]);
    });

    test("deux valeurs consécutives — inchangé", () => {
        expect(expandClasseRange(["1", "2"])).toEqual(["1", "2"]);
    });

    test("sélection avec trou — remplit les valeurs intermédiaires", () => {
        expect(expandClasseRange(["1", "3"])).toEqual(["1", "2", "3"]);
    });

    test("grand écart — remplit toute la plage", () => {
        expect(expandClasseRange(["1", "4"])).toEqual(["1", "2", "3", "4"]);
    });

    test("entrée non triée — trie et remplit", () => {
        expect(expandClasseRange(["3", "1"])).toEqual(["1", "2", "3"]);
    });

    test("plage déjà complète — retourne la même plage triée", () => {
        expect(expandClasseRange(["1", "2", "3"])).toEqual(["1", "2", "3"]);
    });
});
