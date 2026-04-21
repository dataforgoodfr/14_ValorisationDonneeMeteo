import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";
import { defineVitestProject } from "@nuxt/test-utils/config";

export default defineConfig({
    test: {
        globals: true,
        environment: "node",
        environmentOptions: {
            nuxt: {
                dotenv: {
                    fileName: ".env.example",
                },
            },
        },
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
            await defineVitestProject({
                extends: true,
                test: {
                    name: "integration",
                    include: ["app/**/*.integration.test.ts"],
                    environment: "nuxt",
                    testTimeout: 1 * 60 * 1000,
                    environmentOptions: {
                        nuxt: {
                            dotenv: {
                                fileName: ".env.example",
                            },
                        },
                    },
                },
            }),
            await defineVitestProject({
                extends: true,
                test: {
                    name: "e2e",
                    include: ["app/**/*.e2e.test.ts"],
                    environment: "nuxt",
                    testTimeout: 1 * 60 * 1000,
                },
            }),
        ],
    },
    resolve: {
        alias: {
            "~": fileURLToPath(new URL("./app", import.meta.url)),
        },
    },
});
