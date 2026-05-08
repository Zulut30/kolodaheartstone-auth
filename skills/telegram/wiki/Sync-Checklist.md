# Four-format sync checklist

The skill prompt must stay identical across five distribution formats. Full: [docs/SYNC-CHECKLIST.md](https://github.com/Zulut30/telegram-skills/blob/main/docs/SYNC-CHECKLIST.md).

## The five formats

| File | Target |
|---|---|
| `.claude/skills/botforge/SKILL.md` | Claude Code Agent Skill (canonical) |
| `system_prompt.txt` | Raw prompt for any LLM (Anthropic/OpenAI API, Custom GPT, Claude Projects) |
| `cursor/.cursor/rules/botforge.mdc` | Cursor (new MDC format) |
| `cursor/.cursorrules` | Cursor (legacy, kept for older versions) |
| `codex/AGENTS.md` | OpenAI Codex / Codex CLI / Aider / Continue |

## Before any PR touching the skill prompt

- [ ] Updated `SKILL.md`
- [ ] Updated `system_prompt.txt`
- [ ] Updated `cursor/.cursor/rules/botforge.mdc`
- [ ] Updated `cursor/.cursorrules`
- [ ] Updated `codex/AGENTS.md`
- [ ] Sections match: workflow stages, tech standard, hard bans, modes, API constraints

## Before any PR touching only a reference

- [ ] Updated the reference
- [ ] Referenced from `SKILL.md` if new
- [ ] Referenced from `codex/AGENTS.md` "File references" section if new
- [ ] Added to `plugin.json` `references[]` if new

## Before any PR adding a slash command

- [ ] Created `.claude/commands/botforge-<name>.md` with frontmatter
- [ ] Registered in `.claude-plugin/plugin.json` commands array
- [ ] Added row to `.claude/commands/botforge-help.md`
- [ ] Mentioned in root `README.md`
- [ ] CHANGELOG entry under upcoming version

## Automated enforcement

CI (`.github/workflows/validate.yml`) checks:
- Plugin manifest references existing files
- Command markdown files have valid YAML frontmatter with `description`
- **20 canonical concepts** present in all 5 prompt files (`tests/check_sync.py`)

Local check:
```bash
make sync-check
```

## Common drift sources

- Adding a constraint to `SKILL.md` but forgetting `system_prompt.txt`
- Renaming a mode in one file but not others
- Updating Bot API version (9.6 → 9.7) in only `telegram-api-spec.md` without propagating
- Adding a hard ban in prose in one file but not the enforced list in others

## Fast sync technique

1. Edit `SKILL.md` first (canonical).
2. Search the repo for the key phrase you added/changed (Cmd/Ctrl + Shift + F).
3. Propagate to all 5 files.
4. `make sync-check`.
5. Commit.
