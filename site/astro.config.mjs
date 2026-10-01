// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// Public site URL (used by sitemap + absolute URLs).
const SITE_URL = process.env.SITE_URL || "https://sachncs.github.io";

export default defineConfig({
  site: SITE_URL,
  base: "/knowledge",
  trailingSlash: "ignore",
  output: "static",
  integrations: [sitemap()],
  build: {
    assets: "_assets",
    inlineStylesheets: "auto",
  },
  vite: { build: { cssMinify: true } },
  compressHTML: true,
});
