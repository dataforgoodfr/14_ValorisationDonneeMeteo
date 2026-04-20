import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";
import { loadEnv } from "vite";

const env = loadEnv("test", process.cwd(), "");

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
                    env: {
                        NUXT_PUBLIC_API_BASE:
                            env.NUXT_PUBLIC_API_BASE ??
                            "http://localhost:8000/api/v1",
                    },
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
