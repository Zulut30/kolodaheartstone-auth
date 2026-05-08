# Contributing to BotForge

Thanks for helping make the skill better. A few ground rules to keep contributions tight.

## What contributions are welcome

- **New reference modules** in `.claude/skills/botforge/references/` covering additional Telegram features (inline mode extensions, Bot API updates, new payment providers, moderation tools, etc.)
- **New slash commands** in `.claude/commands/`
- **Working examples** in `examples/` — full bot projects that compile, run, pass linters
- **Bug fixes** in existing patterns (outdated API calls, broken HMAC code, etc.)
- **Documentation improvements** — FAQ, troubleshooting, clearer explanations
- **Golden-output tests** in `tests/golden/`

## What is NOT welcome

- Business-logic-in-handlers "variants" — hard ban, not negotiable
- Alternatives to aiogram 3 that require changing the core philosophy (one exception channel: python-telegram-bot mention with ADR justification)
- Broad refactors without prior discussion (open an issue first)
- Untested new code paths in `examples/`

## Development setup

```bash
git clone https://github.com/Zulut30/telegram-skills.git
cd telegram-skills
# No build step — pure markdown.
# Optionally:
pip install pre-commit
pre-commit install
```

## Four-format sync rule

A change to the skill prompt **must** propagate to all four formats:

1. `.claude/skills/botforge/SKILL.md` (canonical)
2. `system_prompt.txt`
3. `cursor/.cursorrules` and `cursor/.cursor/rules/botforge.mdc`
4. `codex/AGENTS.md`

The CI validate workflow checks that key sections appear in all four. Run locally:

```bash
python tests/check_sync.py    # (when harness lands)
```

## Adding a new slash command

1. Create `.claude/commands/botforge-<name>.md` with frontmatter:
   ```yaml
   ---
   description: One-line imperative description
   argument-hint: "[mode] <arg>"
   ---
   ```
2. Body: brief, imperative. Reference applicable `references/*.md`. State hard bans and soft norms inline.
3. Register in `.claude-plugin/plugin.json` → `commands`.
4. Add row to `.claude/commands/botforge-help.md` table.
5. Mention in root `README.md` command listing.
6. Add CHANGELOG entry under the upcoming version.

## Adding a new reference

1. Create `.claude/skills/botforge/references/<topic>.md`.
2. Structure: intro → when to use → architecture impact → code patterns → security checklist → anti-patterns.
3. Every code block runnable (or clearly marked as pseudocode).
4. If the topic has a natural command entry-point, create one (see above).
5. Register the file in `SKILL.md` → `## References` list and in `codex/AGENTS.md`.

## Commit style

- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`
- Subject ≤ 72 chars, imperative mood
- Body explains *why*, not *what* (diff shows the what)
- Reference issues / PRs when applicable

Example:
```
feat(payments): add Stripe subscription recurring example

Users on the SaaS mode needed recurring billing through Stripe's
subscriptions.create API. The provider-agnostic layer stayed intact;
only StripeProvider.create_subscription was added.
```

## PR checklist

- [ ] Four-format sync done (if skill prompt changed)
- [ ] `plugin.json` updated (if command added)
- [ ] CHANGELOG entry added
- [ ] Golden tests pass (if harness exists)
- [ ] Markdown lints (no broken links, valid frontmatter)
- [ ] Screenshots / recordings for DX changes (logos, README updates)

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
