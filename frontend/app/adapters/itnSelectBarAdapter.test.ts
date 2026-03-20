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
        };
    };

describe("useItnSelectBarAdapter", () => {
    beforeEach(() => {
        mockStore = createMockItnStore();
    });

    it("should return adapter with all required properties", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter).toEqual(
            expect.objectContaining({
                granularity: expect.anything(),
                pickedDateStart: expect.anything(),
                pickedDateEnd: expect.anything(),
                sliceTypeSwitchEnabled: expect.anything(),
                sliceType: expect.anything(),
                sliceDatepickerDate: expect.anything(),
                chartRef: expect.anything(),
                data: expect.anything(),
                pending: expect.anything(),
                setGranularity: expect.anything(),
                turnOffSliceType: expect.anything(),
                features: expect.anything(),
            }),
        );
    });

    it("should expose correct feature flags", () => {
        const adapter = useItnSelectBarAdapter();

        expect(adapter.features).toEqual({
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
});
