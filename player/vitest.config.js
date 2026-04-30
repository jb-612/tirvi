// F35/F36 — Vitest config for the vanilla JS player.
// jsdom env so audio elements, DOM APIs, and rAF mocks work.

import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["test/**/*.spec.js"],
    globals: true,
  },
});
