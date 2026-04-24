export default defineAppConfig({
    ui: {
        select: {
            slots: {
                content: "w-auto min-w-(--reka-select-trigger-width)",
            },
        },
        header: {
            slots: {
                root: "bg-dark-950",
            },
        },
        table: {
            slots: {
                tbody: "divide-y divide-blue-350",
                td: "text-blue-350",
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
