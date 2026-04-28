export function useInfoPanel() {
    const isOpen = useState("info-panel-is-open", () => false);
    return {
        isOpen,
        open: () => {
            isOpen.value = true;
        },
        close: () => {
            isOpen.value = false;
        },
    };
}
