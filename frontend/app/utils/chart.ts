/**
 * Returns an array of X-axis indexes for dataZoom synchronization
 * (workaround for xAxisIndex: "all" not being typed)
 */
export function getXAxisIndexes(xAxisLength: number): number[] {
    return Array.from({ length: xAxisLength }, (_, i) => i);
}
