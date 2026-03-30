import { describe, it, expect, beforeEach, vi } from "vitest";
import { ref, shallowRef } from "vue";
import type {
    GranularityType,
    SelectBarAdapter,
} from "~/components/ui/commons/selectBar/types";
import type { NationalIndicatorResponse } from "~/types/api";

// Mock the store
const createMockItnStore = () => ({
    itnChartRef: shallowRef(),
    granularity: ref("month" as const),
    pickedDateStart: ref(new Date(2024, 0, 1)),
    pickedDateEnd: ref(new Date(2024, 11, 31)),
    sliceTypeSwitchEnabled: ref(false),
    sliceType: ref("full" as const),
    sliceDatepickerDate: ref(new Date(2024, 0, 1)),
    itnData: ref(undefined),
    pending: ref(false),
    setGranularity: vi.fn((value: GranularityType) => {
        (mockStore.granularity.value as GranularityType) = value;
    }),
    turnOffSliceType: vi.fn(),
    exportConfig: {
        chartName: "itn",
        csvHeaders: [
            "Date",
            "Température observée en °C (moyenne/valeur selon slice_type)",
            "Température moyenne de référence 1991-2020 pour cette période en °C",
            "Écart-type supérieur en °C (moyenne + 1°C écart-type)",
            "Écart-type inférieur en °C (moyenne - 1°C écart-type)",
            "Température maximale observée sur la période 1991-2020 en °C ",
            "Température minimale observée sur la période 1991-2020 en °C ",
        ],
        getCsvRows: vi.fn(() => undefined),
    },
});

let mockStore: ReturnType<typeof createMockItnStore>;

// Mock the adapter function
const useItnSelectBarAdapter =
    (): SelectBarAdapter<NationalIndicatorResponse> => {
        return {
            granularity: mockStore.granularity,
            pickedDateStart: mockStore.pickedDateStart,
            pickedDateEnd: mockStore.pickedDateEnd,
            sliceTypeSwitchEnabled: mockStore.sliceTypeSwitchEnabled,
            sliceType: mockStore.sliceType,
            sliceDatepickerDate: mockStore.sliceDatepickerDate,
            chartRef: mockStore.itnChartRef,
            data: mockStore.itnData,
            pending: mockStore.pending,
            setGranularity: mockStore.setGranularity,
            turnOffSliceType: mockStore.turnOffSliceType,
            features: {
                hasSliceType: true,
                hasChartTypeSelector: false,
                hasExport: true,
            },
            exportConfig: mockStore.exportConfig,
        };
    };

describe("useItnSelectBarAdapter", () => {
    beforeEach(() => {
        mockStore = createMockItnStore();
    });

    it("should return adapter with all required properties", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter).toMatchObject({
            granularity: expect.objectContaining({ value: expect.any(String) }),
            pickedDateStart: expect.objectContaining({
                value: expect.any(Date),
            }),
            pickedDateEnd: expect.objectContaining({ value: expect.any(Date) }),
            sliceTypeSwitchEnabled: expect.objectContaining({
                value: expect.any(Boolean),
            }),
            sliceType: expect.objectContaining({ value: expect.any(String) }),
            sliceDatepickerDate: expect.objectContaining({
                value: expect.any(Date),
            }),
            chartRef: expect.objectContaining({ value: undefined }),
            data: expect.objectContaining({ value: undefined }),
            pending: expect.objectContaining({ value: expect.any(Boolean) }),
            setGranularity: expect.any(Function),
            turnOffSliceType: expect.any(Function),
            features: expect.any(Object),
        });
    });

    it("should expose correct feature flags", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.features).toMatchObject({
            hasSliceType: true,
            hasChartTypeSelector: false,
            hasExport: true,
        });
    });

    it("should bind setGranularity method from store", () => {
        const adapter = useItnSelectBarAdapter();

        adapter.setGranularity("month");

        expect(mockStore.setGranularity).toHaveBeenCalledWith("month");
        expect(adapter.granularity.value).toBe("month");
    });

    it("should bind turnOffSliceType method from store", () => {
        const adapter = useItnSelectBarAdapter();

        adapter.turnOffSliceType!(false);

        expect(mockStore.turnOffSliceType).toHaveBeenCalledWith(false);
    });

    it("should expose chartRef from store", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.chartRef).toBeDefined();
    });

    it("should expose data from itnData store property", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.data.value).toBeUndefined();
    });

    it("should expose pending state from store", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.pending.value).toBe(false);
    });

    it("should maintain reactivity with store changes", () => {
        const adapter = useItnSelectBarAdapter();

        (mockStore.granularity.value as GranularityType) = "year";

        expect(adapter.granularity.value).toBe("year");
    });

    it("should not expose setChartType method", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.setChartType).toBeUndefined();
    });

    it("should not expose chartType and chartTypeSwitchEnabled properties", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.chartType).toBeUndefined();
        expect(adapter.chartTypeSwitchEnabled).toBeUndefined();
    });

    // Export menu: the adapter must expose exportConfig for the export menu to work
    it("should expose exportConfig object", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.exportConfig).toBeDefined();
    });

    // Export menu: chartName is used to build the downloaded file name
    it("should expose correct chartName in exportConfig", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.exportConfig.chartName).toBe("itn");
    });

    // Export menu: csvHeaders are written as the first row of the exported CSV file
    it("should expose non-empty csvHeaders in exportConfig", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.exportConfig.csvHeaders).toBeInstanceOf(Array);
        expect(adapter.exportConfig.csvHeaders.length).toBeGreaterThan(0);
    });

    // Export menu: getCsvRows is called when the user exports as CSV
    it("should expose getCsvRows as a function in exportConfig", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.exportConfig.getCsvRows).toBeInstanceOf(Function);
    });

    // Export menu: getCsvRows returns undefined when there is no data loaded yet
    it("should return undefined from getCsvRows when itnData is undefined", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.exportConfig.getCsvRows()).toBeUndefined();
    });

    // Export menu: the hasExport feature flag controls visibility of the export button
    it("should have hasExport set to true in features", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.features.hasExport).toBe(true);
    });
});
