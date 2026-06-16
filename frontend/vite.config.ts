/// <reference types="vitest/config" />
import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test-setup.ts",
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      // Measure only our code; the vendored shadcn/agents-ui components are excluded.
      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        "src/components/ui/**",
        "src/components/agents-ui/**",
        "src/components/ai-elements/**",
        "src/hooks/agents-ui/**",
        "src/**/*.test.{ts,tsx}",
        "src/test-setup.ts",
        "src/vite-env.d.ts",
        "src/main.tsx",
      ],
    },
  },
});
