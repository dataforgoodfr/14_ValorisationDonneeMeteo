import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

export default defineConfig({
    test: {
        globals: true,
        environment: "node",
        projects: [
            {
                extends: true,
                test: {
                    name: "unit",
                    include: ["app/**/*.test.ts"],
                    exclude: ["**/*.integration.test.ts", "**/*.e2e.test.ts"],
                    sequence: {
                        concurrent: true,
                    },
                },
            },
            {
                extends: true,
                test: {
                    name: "integration",
                    include: ["app/**/*.integration.test.ts"],
                    testTimeout: 1 * 60 * 1000,
                },
            },
            {
                extends: true,
                test: {
                    name: "e2e",
                    include: ["app/**/*.e2e.test.ts"],
                    testTimeout: 1 * 60 * 1000,
                },
            },
        ],
    },
    resolve: {
        alias: {
            "~": fileURLToPath(new URL("./app", import.meta.url)),
        },
    },
});
