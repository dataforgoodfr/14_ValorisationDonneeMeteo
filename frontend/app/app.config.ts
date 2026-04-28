export default defineAppConfig({
    ui: {
        select: {
            slots: {
                content: "w-auto min-w-(--reka-select-trigger-width)",
            },
        },
        header: {
            slots: {
                root: "dark:bg-dark-950",
            },
        },
        table: {
            slots: {
                tbody: "divide-y dark:divide-blue-350",
                td: "dark:text-blue-350 text-base",
                th: "text-base",
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
