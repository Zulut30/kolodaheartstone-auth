# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 1.x | ✅ |
| <1.0 | ❌ (no such versions) |

## Reporting a vulnerability

**Do not open public GitHub issues for security vulnerabilities.**

Report to: open a [GitHub Security Advisory](https://github.com/Zulut30/telegram-skills/security/advisories/new) (preferred) or contact maintainers via the issue tracker with a minimal reproducer and **without** disclosure details.

You will get an acknowledgment within 72 hours.

## Scope

### In scope
- Vulnerabilities in the skill content that could cause LLMs to generate **insecure code patterns**:
  - Missing HMAC validation snippets
  - Hard-coded secrets in reference templates
  - SQL injection patterns
  - Insecure JWT defaults
  - Missing idempotency in payment examples
- Broken or outdated security guidance in references (`auth.md`, `payments.md`, `miniapp.md`, `telegram-api-spec.md`)
- Vulnerable dependencies in `examples/` working code
- GitHub Actions workflow misconfiguration that could leak secrets

### Out of scope
- Vulnerabilities in **third-party projects** that happened to be generated with BotForge guidance — those are the user's to fix; we'll update guidance if a pattern is systematically unsafe.
- Vulnerabilities in Claude Code, Cursor, Codex, aiogram, Python, or any upstream tool.
- Social engineering against maintainers or contributors.

## Handling process

1. Acknowledgment within **72 hours**.
2. Triage + severity (CVSS) within **7 days**.
3. Fix target:
   - **Critical**: patch + new release within 14 days
   - **High**: within 30 days
   - **Medium / Low**: next minor release
4. Public advisory published after fix ships.
5. Reporter credited (if they wish) in release notes.

## Hardening expectations of users

BotForge generates **code patterns**. Users remain responsible for:

- Rotating `BOT_TOKEN` on schedule
- Storing secrets in password managers / secret managers
- Running `pip-audit` / `safety check` on generated projects
- Reviewing generated code before shipping to production
- Following the embedded Security Checklist (`references/checklists.md`, `references/auth.md`, `references/payments.md`)

A skill can prescribe secure defaults but cannot enforce them at runtime.
