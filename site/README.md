# knowledge project site

The static project site for the [`knowledge`](https://github.com/sachncs/knowledge) Python SDK.

## Stack

- [Astro 5](https://astro.build) static site generation
- TypeScript for the theme toggle
- No client framework or external font service

## Structure

```
site/
├── astro.config.mjs
├── package.json
├── public/                    # Favicon, social preview, robots.txt
└── src/
    ├── components/
    │   └── ThemeToggle.astro
    ├── layouts/
    │   └── BaseLayout.astro   # SEO, social metadata, theme bootstrap
    ├── pages/
    │   └── index.astro        # Project overview and quick start
    └── styles/
        └── global.css         # Base styles and accessible focus treatment
```

## Development

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # static output → dist/
npm run preview  # serve dist/
npm run check    # Astro typecheck
```

## Deployment

Pushing to `master` triggers `.github/workflows/pages.yml`. The site is served
from `/knowledge/`, configured as the Astro `base` path, at
<https://sachncs.github.io/knowledge/>.
