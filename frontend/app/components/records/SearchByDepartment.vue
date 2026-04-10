<script setup lang="ts">
import { departements } from "~/data/records/departements";
import { normalizeString } from "~/utils/string";
import { useRecordsChartStore } from "#imports";

const props = defineProps({
    searchQuery: {
        type: String,
        default: "",
    },
});

const searchQueryRef = toRef(props, "searchQuery");

const store = useRecordsChartStore();
const { departmentsFilter } = storeToRefs(store);
const { setDepartmentFilter } = store;

function onSelectDepartment(
    _event: PointerEvent,
    department: { code: string; name: string },
) {
    setDepartmentFilter(department);
}

const unselectedFilteredDepartments = computed(() => {
    const departmentCodesFilter = departmentsFilter.value;

    return departements.filter((department) => {
        if (!searchQueryRef.value || searchQueryRef.value.trim() === "") {
            return !departmentCodesFilter.includes(department.code);
        }

        const normalizedDepartment = normalizeString(department.name);
        const searchQueryLower = normalizeString(
            searchQueryRef.value,
        ).toLowerCase();
        const departmentNameLower = normalizedDepartment.toLowerCase();
        return (
            !departmentCodesFilter.includes(department.code) &&
            (departmentNameLower.includes(searchQueryLower) ||
                department.code.toLowerCase().includes(searchQueryLower))
        );
    });
});
</script>
<template>
    <div class="overflow-y-auto">
        <ul>
            <li
                v-for="department in unselectedFilteredDepartments"
                :key="`filtered-${department.code}`"
                :title="`${department.name} (${department.code})`"
                class="cursor-pointer pr-2 py-1 text-sm flex items-center justify-between"
                @click="onSelectDepartment($event, department)"
            >
                <span class="truncate"
                    >{{ department.name }} ({{ department.code }})</span
                >
                <UIcon name="i-lucide-plus" class="shrink-0" />
            </li>
        </ul>
    </div>
</template>
