// L'API filtre les classes par min/max, donc sélectionner 1 et 3 doit inclure 2.
export function expandClasseRange(values: string[]): string[] {
    const nums = values.map(Number).sort((a, b) => a - b);
    if (nums.length <= 1) return nums.map(String);
    const min = nums[0]!;
    const max = nums[nums.length - 1]!;
    return Array.from({ length: max - min + 1 }, (_, i) => String(min + i));
}
