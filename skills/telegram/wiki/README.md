# Wiki source

This directory contains the source for the GitHub Wiki at https://github.com/Zulut30/telegram-skills/wiki.

GitHub Wikis are a separate git repo (`<repo>.wiki.git`) — they cannot live in the main repo's branches. These markdown files are the canonical source; `publish_wiki.sh` syncs them to the wiki repo.

## Structure

- `Home.md` — wiki landing (EN)
- `Home-ru.md`, `Home-pl.md` — translated homes
- `_Sidebar.md` — left sidebar shown on every wiki page
- `_Footer.md` — footer shown on every wiki page
- Other `.md` files — individual wiki pages, filename = page title (dashes become spaces in the wiki URL)

Internal links use `[Page Name](Page-Name)` — GitHub Wiki resolves these automatically.

## Publishing

### First time — initialize the wiki

1. Go to https://github.com/Zulut30/telegram-skills/wiki
2. Click "Create the first page" and save (any content) — this creates the `.wiki.git` repo
3. Run `bash wiki/publish_wiki.sh` from repo root to push these files

### Subsequent updates

```bash
bash wiki/publish_wiki.sh
```

The script clones `.wiki.git`, copies every `*.md` from `wiki/` (excluding `README.md`, `publish_wiki.sh`), commits, pushes.

## Editing conventions

- Keep each page ≤ 300 lines. Long references live in the main repo.
- Link to specific files in the main repo via full `https://github.com/Zulut30/...` URLs, not relative paths.
- Sidebar = single source of navigation. Add new pages there.
- Translated versions (`-ru`, `-pl`) should match structure but can skip sections if needed.
