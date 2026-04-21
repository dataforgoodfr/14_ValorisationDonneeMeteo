export default defineAppConfig({
    ui: {
        container: {
            base: "w-full max-w-screen-xl mx-auto",
            padding: "px-2 sm:px-4",
        },
        card: {
            slots: {
                root: "rounded-lg overflow-hidden",
                header: "p-4 pb-0 sm:p-4 sm:pb-0",
                body: "p-4 sm:p-4",
            },
            defaultVariants: {
                variant: "solid",
            },
        },
    },
});
