# Migration Guide

How to upgrade between BotForge versions. Full: [docs/MIGRATION.md](https://github.com/Zulut30/telegram-skills/blob/main/docs/MIGRATION.md).

## SemVer policy

- **Patch (1.x.Y)** — doc edits, typo fixes, example improvements. Always safe.
- **Minor (1.X.0)** — new commands, references, examples, tightened rules. No format changes. Safe to upgrade.
- **Major (X.0.0)** — rule changes that invalidate existing generated bots. Breaking.

No major version is planned. The core philosophy (architecture before code, layered design, hard bans) is stable.

## 1.5 → 1.6 (no breaking changes)

- Tests cleaner (no `__import__` hacks)
- CI Python 3.13 experimental, not blocking
- `install.sh --check` mode
- GitHub Pages landing
- Growth kit infrastructure

Action required: none.

## 1.4 → 1.5 (no breaking changes)

- Example bot now has tests
- Automated four-format sync
- 4 new references: performance, anti-spam, gdpr-compliance, analytics
- `install.sh` one-liner

Action required: none. Contributors: `make sync-check` before PR.

## 1.3 → 1.4

- Trilingual README (EN/RU/PL)
- Golden-output tests harness
- Landing page, logo, OG image
- Comparison doc, showcase

## 1.2 → 1.3

- Working `examples/01-vip-media-bot/`
- Plugin manifest (`plugin.json`)
- 6 new references (scheduler, subscriptions, inline, groups, media, faq)
- Modern Cursor MDC format

Action required: if using `.cursorrules`, optionally switch to `.cursor/rules/botforge.mdc` for newer Cursor.

## 1.1 → 1.2

- Grounded in Bot API 9.6 — stricter rate limit enforcement, Mini App HMAC spec, Telegram Stars XTR currency

Existing bots keep working. New generations enforce official constraints.

## 1.0 → 1.1

- Mini Apps, unified payments, auth layers
- 13 slash commands (previously 0)

Migration: if you called payment providers directly in services, switch to `PaymentProvider` abstraction for multi-provider support.

## Within the same version (patch)

Pull latest:
```bash
git -C ~/.claude/skills/botforge pull
```

Or re-run the installer:
```bash
curl -fsSL https://raw.githubusercontent.com/Zulut30/telegram-skills/main/install.sh | bash
```
