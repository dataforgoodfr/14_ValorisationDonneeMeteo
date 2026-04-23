<script setup lang="ts">
interface Props {
    title: string;
}
const props = defineProps<Props>();
</script>
<template>
    <div class="flex flex-col min-h-5 pb-20">
        <h3 class="flex items-center gap-2 text-slate-500 font-bold">
            {{ props.title }}
        </h3>
<<<<<<< HEAD
        <div class="wrapper py-8 px-4 rounded-xl bg-blue-50 dark:bg-dark-850">
=======
        <div class="wrapper py-8 px-4 rounded-xl dark:bg-dark-850">
>>>>>>> d4c3101 (fix: adjust dark mode colors)
            <slot name="default" />
        </div>
    </div>
</template>
<style>
h3::after {
    content: "";
    flex: 1;
    height: 1px;
    background: currentColor;
    opacity: 0.2;
}
</style>
