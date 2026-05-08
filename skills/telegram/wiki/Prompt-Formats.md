# Prompt Formats

BotForge expects structured prompts. The structure drives the 6-stage workflow.

## Standard format

```
BotForge: [Lite|Pro|Media|SaaS]
Task: <business description>
Constraints: <budget / hosting / deadline>
Answers to brief (optional):
  1) purpose: ...
  2) monetization: ...
  3) audience: ...
  4) integrations: ...
  5) hosting: ...
```

`Pro` is the default if mode is omitted.

## Minimal — let the skill ask

```
BotForge: Pro
Task: VIP bot for a cinema channel
```

The skill will run Stage 1 (Brief) and ask up to 5 questions.

## Full — skip brief

```
BotForge: SaaS
Task: subscription bot for a course marketplace
Constraints: VPS, webhook, launch in 2 weeks
Answers:
  1) purpose: SaaS / VIP access
  2) monetization: ЮKassa subscription 499 RUB/mo
  3) audience: up to 50k MAU
  4) integrations: WordPress catalog sync
  5) hosting: VPS Docker Compose + nginx + Caddy TLS
```

The skill skips Stage 1 and goes straight to ADR.

## Extend

```
BotForge: extend
Task: add a referral program with 20% discount
```

Skill identifies affected layers, proposes diff, migrates data.

## Review

```
BotForge: review app/services/payment_service.py
```

Or paste code directly:

````
BotForge: review

```python
# ... your code ...
```
````

Output: `[blocker]/[major]/[minor]/[nit]` findings with `file:line`.

## Refactor

```
BotForge: refactor

# current code
```

Skill produces PR-sequence plan for zero-downtime migration from monolith.

## Deploy

```
BotForge: deploy fly webhook
```

Concrete commands for Fly.io with webhook mode.

## Anti-patterns

❌ "Make me a Telegram bot" — too vague. Skill will run brief, but answers come out generic.

❌ "Build a bot and add 5 features" — generate first, then extend. Mixed requests break the 6-stage flow.

❌ "Use python-telegram-bot instead of aiogram" without justification — skill will ask why in ADR.

❌ "Skip the ADR" — not allowed. Ask for a shorter ADR instead ("give me a 100-word ADR").
