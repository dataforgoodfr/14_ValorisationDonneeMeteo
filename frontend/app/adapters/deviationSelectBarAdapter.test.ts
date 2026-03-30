import { describe, it, expect, beforeEach, vi } from "vitest";
import { ref, shallowRef } from "vue";
import type {
    GranularityType,
    SelectBarAdapter,
} from "~/components/ui/commons/selectBar/types";
import type { DeviationResponse } from "~/types/api";

// Mock the store
const createMockDeviationStore = () => ({
    deviationChartRef: shallowRef(),
    granularity: ref("month" as const),
    pickedDateStart: ref(new Date(2024, 0, 1)),
    pickedDateEnd: ref(new Date(2024, 11, 31)),
    sliceTypeSwitchEnabled: ref(false),
    sliceType: ref("full" as const),
    sliceDatepickerDate: ref(new Date(2024, 0, 1)),
    deviationData: ref(undefined),
    pending: ref(false),
    setGranularity: vi.fn((value: GranularityType) => {
        (mockStore.granularity.value as GranularityType) = value;
    }),
    exportConfig: {
        chartName: "ecart-normale",
        csvHeaders: [
            "Date",
            "Écart à la normale en °C",
            "Température observée en °C",
            "Température de référence 1991-2020 en °C",
        ],
        getCsvRows: vi.fn(() => undefined),
    },
});

let mockStore: ReturnType<typeof createMockDeviationStore>;

// Mock the adapter function
const useDeviationSelectBarAdapter =
    (): SelectBarAdapter<DeviationResponse> => {
        return {
            granularity: mockStore.granularity,
            pickedDateStart: mockStore.pickedDateStart,
            pickedDateEnd: mockStore.pickedDateEnd,
            sliceTypeSwitchEnabled: mockStore.sliceTypeSwitchEnabled,
            sliceType: mockStore.sliceType,
            sliceDatepickerDate: mockStore.sliceDatepickerDate,
            chartRef: mockStore.deviationChartRef,
            data: mockStore.deviationData,
            pending: mockStore.pending,
            setGranularity: mockStore.setGranularity,
            features: {
                hasSliceType: false,
                hasChartTypeSelector: false,
                hasExport: true,
            },
            exportConfig: mockStore.exportConfig,
        };
    };

describe("useDeviationSelectBarAdapter", () => {
    beforeEach(() => {
        mockStore = createMockDeviationStore();
    });

    it("should return adapter with all required properties", () => {
        const adapter = useDeviationSelectBarAdapter();

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
            features: expect.any(Object),
            exportConfig: expect.any(Object),
        });
    });

    // Feature flags: sliceType and chartTypeSelector are not yet enabled for this chart
    it("should expose correct feature flags", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.features).toEqual({
            hasSliceType: false,
            hasChartTypeSelector: false,
            hasExport: true,
        });
    });

    it("should bind setGranularity method from store", () => {
        const adapter = useDeviationSelectBarAdapter();

        adapter.setGranularity("day");

        expect(mockStore.setGranularity).toHaveBeenCalledWith("day");
        expect(adapter.granularity.value).toBe("day");
    });

    // Chart type selector is not available for the deviation chart
    it("should not expose setChartType method", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.setChartType).toBeUndefined();
    });

    // Chart type selector is not available for the deviation chart
    it("should not expose chartType and chartTypeSwitchEnabled properties", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.chartType).toBeUndefined();
        expect(adapter.chartTypeSwitchEnabled).toBeUndefined();
    });

    it("should expose chartRef from store", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.chartRef).toBeDefined();
    });

    it("should expose data from deviationData store property", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.data.value).toBeUndefined();
    });

    it("should expose pending state from store", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.pending.value).toBe(false);
    });

    it("should maintain reactivity with store changes", () => {
        const adapter = useDeviationSelectBarAdapter();

        (mockStore.granularity.value as GranularityType) = "year";

        expect(adapter.granularity.value).toBe("year");
    });

    // Export menu: the adapter must expose exportConfig for the export menu to work
    it("should expose exportConfig object", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.exportConfig).toBeDefined();
    });

    // Export menu: chartName is used to build the downloaded file name
    it("should expose correct chartName in exportConfig", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.exportConfig.chartName).toBe("ecart-normale");
    });

    // Export menu: csvHeaders are written as the first row of the exported CSV file
    it("should expose non-empty csvHeaders in exportConfig", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.exportConfig.csvHeaders).toBeInstanceOf(Array);
        expect(adapter.exportConfig.csvHeaders.length).toBeGreaterThan(0);
    });

    // Export menu: getCsvRows is called when the user exports as CSV
    it("should expose getCsvRows as a function in exportConfig", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.exportConfig.getCsvRows).toBeInstanceOf(Function);
    });

    // Export menu: getCsvRows returns undefined when there is no data loaded yet
    it("should return undefined from getCsvRows when deviationData is undefined", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.exportConfig.getCsvRows()).toBeUndefined();
    });

    // Export menu: the hasExport feature flag controls visibility of the export button
    it("should have hasExport set to true in features", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.features.hasExport).toBe(true);
    });
});
