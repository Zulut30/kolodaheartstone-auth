# BotForge Landing

Static HTML landing deployed automatically to GitHub Pages on pushes to `main`.

- Live URL: https://zulut30.github.io/telegram-skills/
- Source: [`index.html`](index.html)
- Workflow: [`.github/workflows/pages.yml`](../../.github/workflows/pages.yml)

## Editing

Single file, self-contained (inline CSS). Keep it that way — no build step, no JS dependencies. Load time must stay under 100 KB.

## Assets

Logo and OG image pulled from `assets/logo/` via raw GitHub URLs to avoid duplication.

## Preview locally

```bash
cd docs/landing && python -m http.server 8000
# open http://localhost:8000
```
