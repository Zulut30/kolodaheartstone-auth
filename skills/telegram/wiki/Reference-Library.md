# Reference Library

21 deep-dive modules. Each is standalone, copy-adaptable, cited from the main skill prompt.

Location: [`.claude/skills/botforge/references/`](https://github.com/Zulut30/telegram-skills/tree/main/.claude/skills/botforge/references)

## Core

| Module | Topic |
|---|---|
| [architecture.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/architecture.md) | Full project tree, layer responsibilities, dependency flow |
| [patterns.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/patterns.md) | 12 reusable patterns (settings, DB, middleware, FSM, broadcast, errors) |
| [examples.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/examples.md) | 3 end-to-end generation examples |
| [checklists.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/checklists.md) | Self-review, deploy, security checklists |

## Official API grounding

| Module | Topic |
|---|---|
| [telegram-api-spec.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/telegram-api-spec.md) | Bot API 9.6: rate limits, webhook params, error codes, MarkdownV2, lengths, Mini App HMAC |
| [botfather-setup.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/botfather-setup.md) | Operational checklist: descriptions, scopes, privacy, Mini App registration, token rotation |

## Modules

| Module | Topic |
|---|---|
| [miniapp.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/miniapp.md) | Mini App (initData HMAC, JWT, FastAPI, frontend SDK) |
| [auth.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/auth.md) | Roles, ban, initData, OAuth bridging, API keys |
| [payments.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/payments.md) | Unified PaymentProvider: Stars, ЮKassa, CryptoBot, Stripe, Tribute |
| [subscriptions.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/subscriptions.md) | Recurring billing, trials, proration, dunning, state machine |
| [inline-mode.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/inline-mode.md) | @botname query handler, pagination, chosen_inline_result analytics |
| [groups-and-channels.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/groups-and-channels.md) | Privacy mode, admin rights, forum topics, chat join requests, moderation |
| [media.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/media.md) | Photos/videos/albums/voice, file_id reuse, Local Bot API server |

## Ops & quality

| Module | Topic |
|---|---|
| [scheduler.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/scheduler.md) | APScheduler / arq / cron, expire-subs, reminders, idempotency |
| [observability.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/observability.md) | structlog, Sentry PII scrub, Prometheus, health probes, audit log |
| [performance.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/performance.md) | Connection pools, N+1, batching, file_id reuse, horizontal scaling |
| [anti-spam.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/anti-spam.md) | Captcha, content filters, trust scoring, shadow-ban |
| [analytics.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/analytics.md) | PostHog / Mixpanel, events taxonomy, UTM, A/B |
| [i18n.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/i18n.md) | gettext + Babel, language detection, pluralization |
| [gdpr-compliance.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/gdpr-compliance.md) | /privacy_export, /privacy_delete, retention, breach notification |
| [faq.md](https://github.com/Zulut30/telegram-skills/blob/main/.claude/skills/botforge/references/faq.md) | 20+ troubleshooting entries |

## How references are used

The skill prompt tells the AI: "When generating code for X, read `references/X.md`." The references are included in the skill bundle (Agent Skills for Claude Code) or linked from `AGENTS.md` / `.cursorrules` for other tools.

The AI doesn't memorize 21 files — it consults them just-in-time during generation. This keeps the core prompt lean while giving deep expertise on demand.
