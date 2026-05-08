# CLAUDE.md — BotForge Repository

This repository **is** the BotForge skill itself — meta-context: when you work here, you are editing the skill, not using it.

## Repository shape

```
.claude-plugin/plugin.json          # Claude Code plugin manifest
.claude/skills/botforge/             # The skill itself (SKILL.md + references/)
.claude/commands/                    # 19 slash commands
cursor/                              # Cursor rules (.cursorrules + .cursor/rules/*.mdc)
codex/AGENTS.md                      # Codex / Codex CLI / Aider
docs/                                # INSTALL, USAGE, CHANGELOG, QUICKSTART
examples/                            # Working bot examples
system_prompt.txt                    # Raw prompt for any LLM
SKILL.md                             # Full skill document (mirror)
```

## Editing rules

When modifying skill content, keep the **four formats synchronized**:

1. `.claude/skills/botforge/SKILL.md` — canonical
2. `system_prompt.txt` — raw prompt (Cursor/OpenAI/Anthropic-ready)
3. `cursor/.cursorrules` + `cursor/.cursor/rules/botforge.mdc` — Cursor-specific
4. `codex/AGENTS.md` — Codex / Aider

A change in the system prompt MUST appear in all four. Use `docs/SYNC-CHECKLIST.md` before committing.

## Reference modules

All references live in `.claude/skills/botforge/references/`. Each one is a standalone knowledge unit. When adding a new domain (e.g. "payments-new-provider.md"), also:

- Register it in `SKILL.md` under `## References`
- Add a slash command if the domain deserves its own entry point
- Update `docs/CHANGELOG.md`
- Update `plugin.json` → commands array if new command added

## New slash command checklist

1. Create `.claude/commands/botforge-<name>.md` with YAML frontmatter (`description`, optional `argument-hint`)
2. Register in `plugin.json` commands array
3. Add to `.claude/commands/botforge-help.md` table
4. Add to root `README.md` commands listing

## Testing skill output

Golden tests live in `tests/golden/`. Each test has:
- `prompt.txt` — the user request
- `assertions.yml` — structural expectations (sections present, forbidden patterns absent)

Run: `python tests/run_golden.py` (after implementing harness).

## Publishing

- Version bumped in `plugin.json` AND `docs/CHANGELOG.md`
- `git tag v1.x.y` + `git push --tags`
- GitHub Release with changelog excerpt
- Update `examples/` if breaking changes to patterns

## Philosophy (do not break)

- **Architecture before code.** Skill forces LLM to propose tree before file content.
- **Grounded in official docs.** Every constraint cites `core.telegram.org`.
- **Provider-agnostic where possible.** Payments, auth, storage abstracted behind interfaces.
- **Hard bans are hard.** `requests`, business-logic-in-handlers, secrets-in-code are non-negotiable.
- **Markdown-first.** All skill content is plain markdown — no runtime dependencies.
