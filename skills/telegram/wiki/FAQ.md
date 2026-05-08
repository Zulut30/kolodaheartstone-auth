# FAQ

## Installation

### Skill doesn't activate in Claude Code
1. Ensure you copied the whole `.claude/skills/botforge/` folder, not just `SKILL.md`.
2. Path: `~/.claude/skills/botforge/SKILL.md` (global) or `<project>/.claude/skills/botforge/SKILL.md` (per-project).
3. YAML frontmatter in `SKILL.md` must start with `---` on line 1, have `name` and `description` fields.

### Cursor ignores the rules
- `.cursorrules` is deprecated. Use `.cursor/rules/botforge.mdc` instead.
- In MDC, verify `alwaysApply: true` or specific `globs`.
- Restart Cursor after first install.

### `install.sh` fails on Windows
- Use Git Bash, not PowerShell.
- Run `install.sh --check` first to diagnose.

## Usage

### AI writes a monolith despite BotForge being installed
- Explicitly set mode first line: `BotForge: Pro`.
- Ask for ADR and tree first: "Give me the ADR before any code."
- If still skipping stages, remind: "BotForge requires all 6 stages. Don't skip."

### Output missing ADR / tree / self-review
The LLM tried to "optimize." Reply: "The skill requires all 6 stages including self-review. Regenerate with all stages."

### How do I know output actually follows the skill?
Quick check:
- Sections present: `### ADR`, `### Tree`, `### Self-review`?
- `handlers/` contains SQL or `session.execute`? → blocker.
- `import requests` anywhere? → blocker.
- Secrets in code? `grep -i "token\s*=" app/`
- Dockerfile multi-stage with `USER app` (not root)?

## Runtime errors

### `TelegramBadRequest: message is too long`
Message text limit = 4096 UTF-16 code units. Split or move to Mini App / file.

### `TelegramRetryAfter` frequently
Rate limit violation. Verify:
- Broadcast throttle = 25 msg/s (not 30)
- Per-user = 1 msg/sec
- Group = 20 msg/min

### `TelegramForbiddenError` — what to do?
User blocked the bot. Mark `is_blocked=True` and **don't retry**. It's not an error, it's a state.

### Webhook doesn't receive updates
```bash
curl -s "https://api.telegram.org/bot$TOKEN/getWebhookInfo" | jq
```
Check `last_error_date` and `last_error_message`. Then:
- HTTPS required. Use Let's Encrypt / Caddy / Cloudflare Tunnel.
- Port must be 443, 80, 88, or 8443.
- `secret_token` must match between bot and Telegram settings.
- Firewall not blocking Telegram IPs (149.154.160.0/20, 91.108.4.0/22)?

## Payments

### Telegram Stars invoice doesn't arrive
- `provider_token=""` — literal empty string, not missing.
- `currency="XTR"`, `amount` as integer Stars.
- `payload` comes back in `successful_payment.invoice_payload` — use as `order_id`.
- `pre_checkout_query` **must be answered** with `answer(ok=True)` within 10 seconds.

### Duplicate webhooks activate subscription twice
Your `PaymentRepo.is_processed(external_id)` check isn't called. The BotForge pattern:
```python
if await self._payments.is_processed(external_id):
    return  # idempotent no-op
```

## Deployment

### Alembic: "Target database is not up to date"
```bash
docker compose exec bot alembic current
docker compose exec bot alembic upgrade head
```
Rollback if needed: `alembic downgrade -1`.

### `409 Conflict` on polling
Another bot instance is polling with the same token. Either:
- Stop the other instance
- Switch to webhook (`WEBHOOK_URL` in `.env`)
- Use **separate bots** for dev / staging / prod via BotFather.

### How do I separate dev / staging / prod?
**Three different bots via BotFather.** Not one bot with multiple deployments.

## Mini App

### initData valid but `auth_date` expired
BotForge default TTL = 3600 seconds. If user left Mini App open longer, restart it: `tg.close()` + `tg.openLink(url)`. Frontend auto-relogins.

### CORS errors in browser
- CORS middleware must allow only `https://<webapp-host>`, never `*`.
- Dev: `ngrok http 5173` → add ngrok URL to CORS origins and BotFather Mini App URL.

## i18n

### Language doesn't switch
- Verify `.mo` files compiled: `pybabel compile`.
- Docker: `.mo` must land in the image:
  ```
  COPY --chown=app:app app/locales ./app/locales
  RUN pybabel compile -d app/locales -D bot
  ```

## Performance

### Postgres connection pool exhausted
```python
engine = create_async_engine(url, pool_size=20, max_overflow=40, pool_pre_ping=True)
```
Increase `pool_size` + verify middleware closes sessions (BotForge uses `async with`, so it does).

### Redis loses FSM state
- Verify `RedisStorage`, not `MemoryStorage`.
- `RedisStorage` keeps TTL infinite by default — growth is possible. Periodic cleanup via scheduler.

## Contributing

### I want to add a command / reference / example
See [Contributing](Contributing) and [Four-format sync](Sync-Checklist).

### How do I test skill output?
Golden tests: `python tests/run_golden.py` (needs `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`).

### My PR failed `sync-check` CI
You modified the skill prompt in one format but not others. See [Four-format sync](Sync-Checklist) for the checklist.
