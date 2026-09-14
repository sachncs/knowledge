# knowledge — Product Page

Premium product landing page for the [`knowledge`](https://github.com/sachncs/knowledge) Python SDK,
deployed to GitHub Pages at <https://sachncs.github.io/knowledge/>.

## Stack

- **[Astro 5](https://astro.build)** — static site generator, ships zero JS by default
- **[React 19](https://react.dev)** — interactive islands
- **[Tailwind CSS 3](https://tailwindcss.com)** — design tokens & utilities
- **[Motion](https://motion.dev)** — refined animations
- **TypeScript** strict

## Structure

```
site/
├── astro.config.mjs      # Astro + integrations config (base = /knowledge)
├── tailwind.config.mjs   # Theme tokens (ink, accent, mint)
├── tsconfig.json
├── package.json
├── public/               # Static assets (favicon, og-image, robots, .nojekyll)
└── src/
    ├── layouts/
    │   └── BaseLayout.astro     # SEO, OG, JSON-LD, theme bootstrap
    ├── components/
    │   ├── Nav.astro
    │   ├── Hero.astro           # Hero with animated visual
    │   ├── Features.astro       # 6 feature cards
    │   ├── Workflow.astro       # "How it works" steps + graph
    │   ├── CodePreview.astro    # Tabbed CLI / Python / Output preview
    │   ├── Metrics.astro        # 100% / Any / OKF v0.1 / 2
    │   ├── UseCases.astro       # 6 use cases
    │   ├── FAQ.astro            # Native <details> accordion
    │   ├── CTA.astro            # Final call-to-action
    │   ├── Footer.astro
    │   ├── Logo.astro
    │   └── react/               # Interactive client islands
    │       ├── ThemeToggle.tsx
    │       ├── MobileMenu.tsx
    │       ├── Typewriter.tsx
    │       ├── HeroVisual.tsx
    │       ├── WorkflowVisual.tsx
    │       └── CodeTabs.tsx
    ├── lib/
    │   ├── cn.ts                # className helper
    │   └── reveal.ts            # IntersectionObserver utilities
    ├── pages/
    │   └── index.astro          # Composes all sections
    └── styles/
        └── global.css           # Design system + Tailwind layers
```

## Development

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # static output → dist/
npm run preview  # serve dist/
npm run check    # astro check (typecheck)
```

## Deployment

Pushed to `master` triggers `.github/workflows/pages.yml`, which builds the
site and uploads `site/dist/` as the GitHub Pages artifact.

The site is served from the `/knowledge/` subpath (configured via `base` in
`astro.config.mjs`), matching the GitHub Pages URL pattern
`https://<owner>.github.io/knowledge/`.

## Design system

| Token | Value | Use |
| --- | --- | --- |
| `--bg`, `--bg-soft`, `--bg-elev` | Canvas palette | Page backgrounds |
| `--fg`, `--fg-muted`, `--fg-subtle` | Ink palette | Foreground text |
| `--accent`, `--accent-soft` | `#5B6BF2` family | CTAs, links, highlights |
| `--border`, `--border-strong` | Hairline rules | Cards, dividers |
| `font-sans` | Inter | Body + UI |
| `font-mono` | JetBrains Mono | Code, metadata |

Light/dark tokens are CSS custom properties that flip via the `.dark` class on
`<html>`, applied at first paint by an inline script that respects
`localStorage` and `prefers-color-scheme`.