# Four-format sync checklist

The skill prompt must stay identical across four deployment formats. Use this checklist before any commit that changes skill behavior.

## The four formats

| File | Target |
|---|---|
| `.claude/skills/botforge/SKILL.md` | Claude Code Agent Skill (canonical) |
| `system_prompt.txt` | Raw prompt for any LLM (Anthropic/OpenAI API, Custom GPT, Claude Projects) |
| `cursor/.cursor/rules/botforge.mdc` | Cursor (new MDC format) |
| `cursor/.cursorrules` | Cursor (legacy, kept for older versions) |
| `codex/AGENTS.md` | OpenAI Codex / Codex CLI / Aider / Continue |

## Before committing

If your change touches the **skill prompt**, sync across all 5 files:

- [ ] Updated `SKILL.md`
- [ ] Updated `system_prompt.txt`
- [ ] Updated `cursor/.cursor/rules/botforge.mdc`
- [ ] Updated `cursor/.cursorrules`
- [ ] Updated `codex/AGENTS.md`
- [ ] Sections match: workflow stages, tech standard, hard bans, modes, API constraints

If your change touches **only a reference file** (`.claude/skills/botforge/references/*.md`):

- [ ] Updated the reference
- [ ] Referenced from `SKILL.md` if new
- [ ] Referenced from `codex/AGENTS.md` "File references" section if new
- [ ] Added to `plugin.json` `references` array if new

If your change adds a **new slash command**:

- [ ] Created `.claude/commands/botforge-<name>.md` with frontmatter
- [ ] Registered in `.claude-plugin/plugin.json` commands array
- [ ] Added row to `.claude/commands/botforge-help.md`
- [ ] Mentioned in root `README.md`
- [ ] Added entry to `CHANGELOG.md`

## Automated enforcement

CI (`.github/workflows/validate.yml`) checks:
- `plugin.json` references existing files
- Command markdown files have valid YAML frontmatter with `description`
- Markdown files lint clean

A future check (TODO) will diff key sections across the four skill-prompt files and fail PRs with drift.

## Common drift sources

- Adding a constraint to `SKILL.md` but forgetting `system_prompt.txt`
- Renaming a mode in one file but not others
- Updating Bot API version (9.6 → 9.7) in only `telegram-api-spec.md` without propagating to system prompts

## Fast sync tip

Cmd/Ctrl + Shift + F on the repo for `Bot API 9.6` or any versioned token → ensure all matches update together.
