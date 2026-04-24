export default defineAppConfig({
    ui: {
        select: {
            slots: {
                content: "w-auto min-w-(--reka-select-trigger-width)",
            },
        },
        card: {
            slots: {
                root: "rounded-lg overflow-hidden",
                header: "p-4 pb-0 sm:p-4 sm:pb-0",
                body: "p-4 sm:p-4",
            },
        },
    },
});
