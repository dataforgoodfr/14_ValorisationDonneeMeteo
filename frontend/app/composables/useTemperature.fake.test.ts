import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { ref, nextTick } from "vue";
import { useTemperatureRecordsFake } from "~/composables/useTemperature.fake";

// Advance past the 600 ms debounce so data is populated.
function flush() {
    vi.advanceTimersByTime(600);
}

describe("useTemperatureRecordsFake", () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    // --- Defaults ---

    it("returns all 30 stations when no filters are applied", () => {
        const { data } = useTemperatureRecordsFake({});
        flush();
        expect(data.value?.count).toBe(30);
    });

    it("defaults to hot records", () => {
        const { data } = useTemperatureRecordsFake({});
        flush();
        const stations = data.value?.stations ?? [];
        expect(stations.every((s) => s.cold_records.length === 0)).toBe(true);
        expect(stations.every((s) => s.hot_records.length > 0)).toBe(true);
    });

    it("defaults to a limit of 10 stations", () => {
        const { data } = useTemperatureRecordsFake({});
        flush();
        expect(data.value?.stations.length).toBe(10);
    });

    // --- type_records filter ---

    it("returns only hot records when type_records is 'hot'", () => {
        const { data } = useTemperatureRecordsFake({ type_records: "hot" });
        flush();
        const stations = data.value?.stations ?? [];
        expect(stations.length).toBeGreaterThan(0);
        expect(stations.every((s) => s.hot_records.length > 0)).toBe(true);
        expect(stations.every((s) => s.cold_records.length === 0)).toBe(true);
    });

    it("returns only cold records when type_records is 'cold'", () => {
        const { data } = useTemperatureRecordsFake({ type_records: "cold" });
        flush();
        const stations = data.value?.stations ?? [];
        expect(stations.length).toBeGreaterThan(0);
        expect(stations.every((s) => s.cold_records.length > 0)).toBe(true);
        expect(stations.every((s) => s.hot_records.length === 0)).toBe(true);
    });

    it("returns both hot and cold records when type_records is 'all'", () => {
        const { data } = useTemperatureRecordsFake({
            type_records: "all",
            limit: 30,
        });
        flush();
        const stations = data.value?.stations ?? [];
        expect(stations.every((s) => s.hot_records.length > 0)).toBe(true);
        expect(stations.every((s) => s.cold_records.length > 0)).toBe(true);
    });

    // --- station_ids filter ---

    it("filters by a single station id", () => {
        const { data } = useTemperatureRecordsFake({
            station_ids: ["34129001"],
        });
        flush();
        expect(data.value?.count).toBe(1);
        expect(data.value?.stations[0]?.id).toBe("34129001");
    });

    it("filters by multiple station ids", () => {
        const { data } = useTemperatureRecordsFake({
            station_ids: ["34129001", "55001001"],
        });
        flush();
        expect(data.value?.count).toBe(2);
        const ids = data.value?.stations.map((s) => s.id);
        expect(ids).toContain("34129001");
        expect(ids).toContain("55001001");
    });

    it("returns 0 stations when station_ids has no match", () => {
        const { data } = useTemperatureRecordsFake({
            station_ids: ["nonexistent"],
        });
        flush();
        expect(data.value?.count).toBe(0);
    });

    // --- departments filter ---

    it("filters by department", () => {
        // departement "64" has two fake stations (Pau and Biarritz)
        const { data } = useTemperatureRecordsFake({ departments: ["64"] });
        flush();
        expect(data.value?.count).toBe(2);
        expect(
            data.value?.stations.every((_) =>
                data.value?.metadata.departments.includes("64"),
            ),
        ).toBe(true);
    });

    it("returns 0 stations when department has no match", () => {
        const { data } = useTemperatureRecordsFake({ departments: ["99"] });
        flush();
        expect(data.value?.count).toBe(0);
    });

    it("combines station_ids and departments filters (intersection)", () => {
        // "34129001" is in departement "94", not "75"
        const { data } = useTemperatureRecordsFake({
            station_ids: ["34129001"],
            departments: ["75"],
        });
        flush();
        expect(data.value?.count).toBe(0);
    });

    // --- date range filter ---

    it("filters records by date_start", () => {
        const { data } = useTemperatureRecordsFake({
            type_records: "all",
            date_start: "2010-01-01",
            limit: 30,
        });
        flush();
        for (const s of data.value?.stations ?? []) {
            for (const r of [...s.hot_records, ...s.cold_records]) {
                expect(r.date >= "2010-01-01").toBe(true);
            }
        }
    });

    it("filters records by date_end", () => {
        const { data } = useTemperatureRecordsFake({
            type_records: "all",
            date_end: "1985-12-31",
            limit: 30,
        });
        flush();
        for (const s of data.value?.stations ?? []) {
            for (const r of [...s.hot_records, ...s.cold_records]) {
                expect(r.date <= "1985-12-31").toBe(true);
            }
        }
    });

    it("excludes a station when all its records fall outside the date range", () => {
        // All fake records have dates between 1980 and 2026; this range matches none.
        const { data } = useTemperatureRecordsFake({
            date_start: "1900-01-01",
            date_end: "1900-12-31",
        });
        flush();
        expect(data.value?.count).toBe(0);
    });

    // --- temperature range filter ---

    it("filters hot records by temperature_min", () => {
        const { data } = useTemperatureRecordsFake({
            type_records: "hot",
            temperature_min: 41,
            limit: 30,
        });
        flush();
        for (const s of data.value?.stations ?? []) {
            for (const r of s.hot_records) {
                expect(r.value).toBeGreaterThanOrEqual(41);
            }
        }
    });

    it("filters cold records by temperature_max", () => {
        const { data } = useTemperatureRecordsFake({
            type_records: "cold",
            temperature_max: -20,
            limit: 30,
        });
        flush();
        for (const s of data.value?.stations ?? []) {
            for (const r of s.cold_records) {
                expect(r.value).toBeLessThanOrEqual(-20);
            }
        }
    });

    // --- pagination ---

    it("count reflects total filtered results, not just the current page", () => {
        const { data } = useTemperatureRecordsFake({ limit: 5 });
        flush();
        expect(data.value?.count).toBe(30);
        expect(data.value?.stations.length).toBe(5);
    });

    it("offset skips the correct number of stations", () => {
        const { data: all } = useTemperatureRecordsFake({ limit: 30 });
        flush();
        const { data: paged } = useTemperatureRecordsFake({
            limit: 5,
            offset: 5,
        });
        flush();
        expect(paged.value?.stations[0]?.id).toBe(all.value?.stations[5]?.id);
    });

    it("returns an empty page when offset exceeds count", () => {
        const { data } = useTemperatureRecordsFake({ limit: 10, offset: 100 });
        flush();
        expect(data.value?.stations.length).toBe(0);
    });

    // --- metadata ---

    it("station_ids and departments in metadata are parallel arrays", () => {
        const { data } = useTemperatureRecordsFake({ limit: 30 });
        flush();
        const meta = data.value?.metadata;
        expect(meta).toBeDefined();
        expect(meta!.station_ids.length).toBe(meta!.departments.length);
    });

    it("metadata reflects the applied filters", () => {
        const { data } = useTemperatureRecordsFake({
            type_records: "cold",
            temperature_max: -15,
            date_start: "1990-01-01",
        });
        flush();
        const meta = data.value?.metadata;
        expect(meta).toBeDefined();
        expect(meta!.type_records).toBe("cold");
        expect(meta!.temperature_max).toBe(-15);
        expect(meta!.date_start).toBe("1990-01-01");
    });

    // --- pending state ---

    it("is pending while the debounce timer is running", () => {
        const { pending } = useTemperatureRecordsFake({});
        expect(pending.value).toBe(true);
    });

    it("clears pending state after the debounce fires", () => {
        const { pending } = useTemperatureRecordsFake({});
        flush();
        expect(pending.value).toBe(false);
    });

    // --- reactivity ---

    it("recomputes when reactive params change", async () => {
        const params = ref({ station_ids: ["34129001"] });
        const { data } = useTemperatureRecordsFake(params);
        flush();
        expect(data.value?.count).toBe(1);

        params.value = { station_ids: ["34129001", "55001001"] };
        // Vue's watch scheduler runs as a microtask — flush it before advancing the timer.
        await nextTick();
        flush();
        expect(data.value?.count).toBe(2);
    });
});
