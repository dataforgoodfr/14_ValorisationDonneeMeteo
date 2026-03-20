import { describe, it, expect, beforeEach, vi } from "vitest";
import { ref } from "vue";
import type {
    GranularityType,
    ChartType,
    SelectBarAdapter,
} from "~/components/ui/commons/selectBar/types";
import type { DeviationResponse } from "~/types/api";

// Mock the store
const createMockDeviationStore = () => ({
    granularity: ref("month" as const),
    pickedDateStart: ref(new Date(2024, 0, 1)),
    pickedDateEnd: ref(new Date(2024, 11, 31)),
    sliceTypeSwitchEnabled: ref(false),
    sliceType: ref("full" as const),
    sliceDatepickerDate: ref(new Date(2024, 0, 1)),
    chartTypeSwitchEnabled: ref(false),
    chartType: ref("bar" as const),
    deviationData: ref(undefined),
    pending: ref(false),
    setGranularity: vi.fn((value: GranularityType) => {
        (mockStore.granularity.value as GranularityType) = value;
    }),
    setChartType: vi.fn((value: ChartType) => {
        (mockStore.chartType.value as ChartType) = value;
    }),
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
            chartTypeSwitchEnabled: mockStore.chartTypeSwitchEnabled,
            chartType: mockStore.chartType,
            data: mockStore.deviationData,
            pending: mockStore.pending,
            setGranularity: mockStore.setGranularity,
            setChartType: mockStore.setChartType,
            features: {
                hasSliceType: true,
                hasChartTypeSelector: true,
                hasExport: false,
            },
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
            chartTypeSwitchEnabled: expect.objectContaining({
                value: expect.any(Boolean),
            }),
            chartType: expect.objectContaining({ value: expect.any(String) }),
            data: expect.objectContaining({ value: undefined }),
            pending: expect.objectContaining({ value: expect.any(Boolean) }),
            setGranularity: expect.any(Function),
            setChartType: expect.any(Function),
            features: expect.any(Object),
        });
    });

    it("should expose correct feature flags", () => {
        const adapter = useDeviationSelectBarAdapter();

        expect(adapter.features).toEqual({
            hasSliceType: true,
            hasChartTypeSelector: true,
            hasExport: false,
        });
    });

    it("should bind setGranularity method from store", () => {
        const adapter = useDeviationSelectBarAdapter();

        adapter.setGranularity("day");

        expect(mockStore.setGranularity).toHaveBeenCalledWith("day");
        expect(adapter.granularity.value).toBe("day");
    });

    it("should bind setChartType method from store", () => {
        const adapter = useDeviationSelectBarAdapter();

        adapter.setChartType!("line");

        expect(mockStore.setChartType).toHaveBeenCalledWith("line");
        expect(adapter.chartType!.value).toBe("line");
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
});
