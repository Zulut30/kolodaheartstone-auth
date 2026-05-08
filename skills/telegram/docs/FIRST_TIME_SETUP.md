# First-time GitHub setup

BotForge ships two things that GitHub cannot auto-enable: **Pages** and **Wiki**. Each needs **one click** in the repo's Settings. After that, everything syncs automatically.

## 1. GitHub Pages (landing at zulut30.github.io/telegram-skills)

### Option A — via repo settings (reliable, 10 seconds)

1. Open https://github.com/Zulut30/telegram-skills/settings/pages
2. Under **Source**, select **"GitHub Actions"**
3. Save

The `pages` workflow will run automatically (or trigger it manually: Actions tab → `pages` → **Run workflow**).

After ~1 minute:
- Landing: https://zulut30.github.io/telegram-skills/

### Option B — verify deployment

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://zulut30.github.io/telegram-skills/
```
- `200` = live
- `404` = still not enabled (see Option A)

### If the `pages` workflow keeps failing

Common cause: the `enablement: true` flag in `configure-pages` requires admin-scoped GITHUB_TOKEN on some org-owned repos. Simply enable Pages manually via Option A — after that, deployments work with default `GITHUB_TOKEN`.

## 2. GitHub Wiki

### Initialize the wiki (one-time)

GitHub creates the separate `<repo>.wiki.git` repo only after the first page is saved via the web UI.

1. Open https://github.com/Zulut30/telegram-skills/wiki
2. Click **"Create the first page"**
3. Title: anything (`Home` is fine — will be overwritten)
4. Content: anything (`temporary` is fine)
5. Click **"Save Page"**

### Sync the 19 pages

After the first save, two things are triggered:

**Automatic (recommended)** — push any change to `wiki/` on main, and the [`wiki` workflow](../.github/workflows/wiki.yml) syncs using [Andrew-Chen-Wang/github-wiki-action](https://github.com/marketplace/actions/github-wiki-action). You can also trigger it manually:

- Go to Actions tab → `wiki` → **Run workflow**
- All 19 pages land in the wiki in ~30 seconds

**Manual fallback** — run the script locally:
```bash
cd telegram-skills
bash wiki/publish_wiki.sh
```

## 3. GitHub Discussions (optional but recommended)

1. Open https://github.com/Zulut30/telegram-skills/settings
2. Scroll to **Features** → check **Discussions** → Set up
3. Categories are created automatically (Announcements, Q&A, Show and tell, Ideas, Polls)
4. Discussion templates in `.github/DISCUSSION_TEMPLATE/` are picked up on first post

Seed content ready: [`.github/GROWTH_KIT.md`](../.github/GROWTH_KIT.md) has 5 discussion starters + 10 seeded issues.

## 4. GitHub Actions secrets (optional)

To enable **golden tests** on PRs:

1. Open https://github.com/Zulut30/telegram-skills/settings/secrets/actions
2. Add repository secret: `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`)
3. The `golden` workflow will run on every PR

Without the secret, the workflow gracefully skips.

## 5. Dependabot (already configured)

`.github/dependabot.yml` is in the repo. Dependabot starts automatically on push. No action needed.

## 6. Branch protection (recommended for multi-contributor repos)

1. https://github.com/Zulut30/telegram-skills/settings/branches
2. Add rule for `main`:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass: `validate`, `frontmatter`, `sync-check`, `plugin-manifest`, `example-bot-tests` (3.12)
   - ✅ Require branches to be up to date before merging
3. Save

## TL;DR

Five clicks:
1. Settings → Pages → Source: GitHub Actions
2. Wiki → Create the first page → Save
3. Actions → Run `pages` workflow
4. Actions → Run `wiki` workflow
5. (Optional) Settings → Features → Discussions

Done. Landing live, wiki populated, community channel open.
