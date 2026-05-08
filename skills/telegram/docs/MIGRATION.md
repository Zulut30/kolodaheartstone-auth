# Migration Guide

How to upgrade between BotForge versions.

## 1.4 → 1.5 (no breaking changes)

**What's new:**
- Example bot now has `pytest` test suite (unit + integration)
- `tests/check_sync.py` — automated four-format sync check
- `install.sh` one-liner installer
- `Makefile` at repo root for contributors
- `.github/dependabot.yml` enabled
- `plugin.json` — removed non-standard `$comment` field

**Action required:** none for end users. For contributors:
```bash
make sync-check        # verify skill prompt consistency
make example-test      # run example bot tests
```

## 1.3 → 1.4 (no breaking changes)

**What's new:**
- Trilingual README (EN / RU / PL)
- Golden-output eval harness in `tests/golden/`
- `assets/logo/` with SVG mark + OG image
- `.vscode/` snippets, `.zed/` config
- `docs/COMPARISON.md`, `docs/SHOWCASE.md`, `docs/SYNC-CHECKLIST.md`
- `.github/CODEOWNERS`, `FUNDING.yml`, `release.yml`

**Action required:** none.

## 1.2 → 1.3 (major expansion)

**What's new:**
- `.claude-plugin/plugin.json` — Claude Code plugin manifest
- **Working example** at `examples/01-vip-media-bot/` (~25 Python files)
- 6 new reference modules: scheduler, subscriptions, inline-mode, groups-and-channels, media, faq
- 2 new slash commands: `/botforge-scheduler`, `/botforge-inline`
- Governance files: SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md
- `cursor/.cursor/rules/botforge.mdc` — modern Cursor MDC format

**Action required:** nothing breaks. But:
- If you used `.cursorrules` — switch to the new MDC file for better Cursor support.
- If you want plugin auto-install when available — run `/plugin install github:Zulut30/telegram-skills` in Claude Code.

## 1.1 → 1.2 (non-breaking, guarantees tightened)

**What's new:**
- Skill grounded in official Bot API 9.6 (rate limits, Mini App initData HMAC, error-code handling).
- New references: telegram-api-spec, botfather-setup, i18n, observability.
- 3 new commands: `/botforge-botfather`, `/botforge-i18n`, `/botforge-observability`.

**Action required:** existing bots unaffected. New generations enforce stricter Bot API rules.

## 1.0 → 1.1 (non-breaking, major feature add)

**What's new:**
- `references/miniapp.md`, `references/auth.md`, `references/payments.md`
- 13 slash commands (was 0 — previously only in SKILL.md prose).
- Unified `PaymentProvider` interface for Stars / ЮKassa / CryptoBot / Stripe / Tribute.

**Action required:** if you were calling payment provider APIs directly in services, switch to the `PaymentProvider` abstraction for easier multi-provider support.

## Skill prompt philosophy (unchanged since 1.0)

These invariants never change:
- Architecture before code.
- 6-stage workflow mandatory.
- Hard bans on `requests`, secrets, SQL-in-handlers, monoliths.
- aiogram 3 as default stack.

Any breaking change to these would be a **major-version** bump (2.0), not a minor.

## Breaking-change policy

BotForge follows [SemVer](https://semver.org/):
- **Patch (1.x.Y)** — doc edits, typo fixes, example improvements.
- **Minor (1.X.0)** — new commands, new references, new examples, tightened rules. No format changes.
- **Major (X.0.0)** — rule changes that invalidate existing generated bots (e.g., forced migration to new architecture layer).

We currently have no major-version changes planned.
