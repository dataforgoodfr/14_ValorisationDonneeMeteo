<script setup lang="ts">
import departments from "./departments.json";

const store = useRecordsGraphStore();
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
    return departments.filter((d) => !departmentCodesFilter.includes(d.code));
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
