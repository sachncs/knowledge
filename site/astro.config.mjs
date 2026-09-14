// @ts-check
import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import tailwind from "@astrojs/tailwind";
import sitemap from "@astrojs/sitemap";

// Public site URL (used by sitemap + absolute URLs).
const SITE_URL = process.env.SITE_URL || "https://sachncs.github.io";

export default defineConfig({
  site: SITE_URL,
  base: "/knowledge",
  trailingSlash: "ignore",
  output: "static",
  integrations: [
    react(),
    tailwind({
      applyBaseStyles: false,
    }),
    sitemap(),
  ],
  build: {
    assets: "_assets",
    inlineStylesheets: "auto",
  },
  vite: {
    build: {
      cssMinify: true,
    },
    ssr: {
      noExternal: ["motion"],
    },
  },
  compressHTML: true,
});