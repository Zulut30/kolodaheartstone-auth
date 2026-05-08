# Security

Full policy: [SECURITY.md](https://github.com/Zulut30/telegram-skills/blob/main/SECURITY.md).

## Reporting a vulnerability

**Do not open public issues for security problems.**

Preferred: open a [GitHub Security Advisory](https://github.com/Zulut30/telegram-skills/security/advisories/new).

Alternatives: see [`.well-known/security.txt`](https://github.com/Zulut30/telegram-skills/blob/main/.well-known/security.txt) (RFC 9116).

Response: acknowledgment within 72 hours.

## Scope

### In scope
- Skill patterns that generate insecure code (missing HMAC, hardcoded secrets in references, SQL injection, insecure JWT defaults, missing payment idempotency)
- Broken or outdated security guidance in references
- Vulnerable dependencies in `examples/` code
- GitHub Actions misconfiguration that could leak secrets

### Out of scope
- Vulnerabilities in **your** bot that happened to be generated with BotForge — those are yours to fix. We'll update guidance if a pattern is systematically unsafe.
- Upstream vulnerabilities (aiogram, Python, Claude Code, Cursor, Codex).
- Social engineering.

## Severity targets

- **Critical** — patch + release within 14 days
- **High** — within 30 days
- **Medium / Low** — next minor release

## User responsibilities

BotForge generates code patterns. As a user:
- Rotate `BOT_TOKEN` on a schedule (quarterly minimum)
- Store secrets in password managers / secret managers, never in code
- Run `pip-audit` / `safety check` on generated bots regularly
- Review generated code before shipping
- Follow embedded security checklists in references

## Acknowledgments

Researchers who reported issues responsibly: [SECURITY_THANKS.md](https://github.com/Zulut30/telegram-skills/blob/main/docs/SECURITY_THANKS.md).
