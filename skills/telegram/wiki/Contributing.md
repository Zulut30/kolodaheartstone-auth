# Contributing

Short version: see [CONTRIBUTING.md](https://github.com/Zulut30/telegram-skills/blob/main/CONTRIBUTING.md) in the repo.

This page has the Wiki-friendly tour.

## What contributions are welcome

- **New reference modules** covering Telegram features we don't cover
- **New slash commands**
- **Working examples** in `examples/`
- **Bug fixes** in existing patterns
- **Documentation** improvements, translations
- **Golden tests** (`tests/golden/`)

## What is NOT welcome

- Business-logic-in-handlers variants — hard ban
- Alternatives to aiogram that require changing core philosophy
- Broad refactors without prior issue
- Untested new code paths in `examples/`

## Development setup

```bash
git clone https://github.com/Zulut30/telegram-skills.git
cd telegram-skills
pip install pre-commit
pre-commit install
```

No build step — pure markdown, Python validators, and bash.

## Four-format sync rule

Skill prompt lives in **five** places:
1. `.claude/skills/botforge/SKILL.md` (canonical)
2. `system_prompt.txt`
3. `cursor/.cursor/rules/botforge.mdc`
4. `cursor/.cursorrules`
5. `codex/AGENTS.md`

Any change to skill prompt → all five updated. CI's `sync-check` job enforces it.

Run locally:
```bash
make sync-check
```

See [Sync-Checklist](Sync-Checklist) for details.

## Adding a new slash command

1. Create `.claude/commands/botforge-<name>.md` with YAML frontmatter:
   ```yaml
   ---
   description: One-line imperative description
   argument-hint: "[mode] <arg>"
   ---
   ```
2. Body: brief, imperative. Reference applicable `references/*.md`. Include hard bans inline.
3. Register in `.claude-plugin/plugin.json` → `commands`.
4. Add row to `.claude/commands/botforge-help.md` table.
5. Mention in root `README.md` command listing.
6. CHANGELOG entry under upcoming version.

## Adding a new reference

1. Create `.claude/skills/botforge/references/<topic>.md`.
2. Structure: intro → when to use → architecture impact → code patterns → security checklist → anti-patterns.
3. Every code block runnable or clearly marked pseudocode.
4. If the topic has a natural entry-point, add a slash command.
5. Register in `SKILL.md` → `## References` and in `codex/AGENTS.md` references list.
6. Add to `plugin.json` `references[]`.

## Commit style

Conventional commits:
- `feat:` new feature / reference / command
- `fix:` bugfix
- `docs:` documentation
- `refactor:` internal restructuring
- `test:` test additions
- `chore:` maintenance

Subject ≤ 72 chars, imperative mood. Body explains *why*.

## PR checklist

- [ ] Four-format sync done (if skill prompt changed)
- [ ] `plugin.json` updated (if command added)
- [ ] CHANGELOG entry added under upcoming version
- [ ] Golden tests pass (or gracefully skip)
- [ ] Markdown lints clean
- [ ] Example bot tests green (if examples/ changed)

## Governance

- Seeded issues and roadmap: see [Growth Kit](https://github.com/Zulut30/telegram-skills/blob/main/.github/GROWTH_KIT.md).
- Security disclosure: [Security](Security).
- Code of conduct: [Contributor Covenant 2.1](https://github.com/Zulut30/telegram-skills/blob/main/CODE_OF_CONDUCT.md).
