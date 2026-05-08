<p align="center">
  <img src="../../assets/logo/logo.svg" width="128" alt="BotForge logo" />
</p>

<h1 align="center">BotForge</h1>

<p align="center">
  <b>Inżynierski skill dla AI, tworzący production-ready boty Telegrama</b><br/>
  Gotowy pakiet dla Claude Code, Codex, Cursora i dowolnego LLM.
</p>

<p align="center">
  <a href="../../README.md">English</a> · <a href="../ru/README.md">Русский</a> · <b>Polski</b>
</p>

<p align="center">
  <a href="../QUICKSTART.md">Szybki start</a> ·
  <a href="../INSTALL.md">Instalacja</a> ·
  <a href="../USAGE.md">Użycie</a> ·
  <a href="../COMPARISON.md">Porównanie</a> ·
  <a href="../SHOWCASE.md">Przykłady</a>
</p>

<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"/></a>
  <a href="https://claude.com/claude-code"><img src="https://img.shields.io/badge/Claude%20Code-compatible-8A2BE2" alt="Claude Code"/></a>
  <a href="https://cursor.com"><img src="https://img.shields.io/badge/Cursor-rules-000000" alt="Cursor"/></a>
  <a href="https://openai.com"><img src="https://img.shields.io/badge/Codex-AGENTS.md-10A37F" alt="Codex"/></a>
  <a href="https://docs.aiogram.dev/"><img src="https://img.shields.io/badge/aiogram-3.x-2CA5E0" alt="aiogram"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12%2B-3776AB" alt="Python"/></a>
  <a href="https://core.telegram.org/bots/api"><img src="https://img.shields.io/badge/Bot%20API-9.6-0088CC" alt="Bot API"/></a>
</p>

---

BotForge zamienia asystenta AI w doświadczonego inżyniera botów Telegrama. Zamiast jednorazowego `main.py` z 800 linijkami splątanego kodu, AI projektuje i buduje **modularnego, skalowalnego, production-ready bota Telegrama** — z architekturą, bazą danych, migracjami, panelem admina, płatnościami, broadcastami, Dockerem i deploymentem.

## Trzy obietnice

1. **Żadnych monolitów.** Warstwowa architektura (handlers / services / repositories / integrations) od razu.
2. **Żadnych szkiców.** Docker + Postgres + Alembic + `.env` + instrukcje deploymentu już w pierwszej generacji.
3. **Nic się nie rozpadnie.** Piątą funkcję dodaje się tak samo łatwo jak pierwszą.

## Dlaczego to działa

- **Oparty na oficjalnej dokumentacji Telegram Bot API 9.6.** Limity rate (1/s, 20/min, 30/s broadcast), zasady escape MarkdownV2, walidacja HMAC initData dla Mini Apps, limit 64 bajtów `CallbackData` — każde ograniczenie cytuje `core.telegram.org`.
- **Obowiązkowy 6-etapowy workflow.** Brief → ADR → Tree → Files → Self-review → Deploy. AI nie może przejść od razu do kodu.
- **Twarde zakazy wymuszane przez reguły skilla.** Sekrety w kodzie, `requests`, SQL w handlerach, monolity — blokowane na poziomie skilla, nie stylu.
- **Płatności niezależne od providera.** Zmiana ЮKassa → Stripe to jedna linia DI.

## Szybki start

```bash
git clone https://github.com/Zulut30/telegram-skills.git
cp -r telegram-skills/.claude/skills/botforge ~/.claude/skills/
cp -r telegram-skills/.claude/commands ~/.claude/
```

W Claude Code:
```
/botforge-new SaaS
Zadanie: bot-sklep z kursami online z dostępem VIP za 99 PLN/miesiąc
Hosting: VPS, Docker Compose, webhook
```

AI zada do 5 pytań doprecyzowujących, przygotuje ADR, wygeneruje drzewo projektu, stworzy wszystkie pliki, przejdzie self-review i poda komendy deploymentu.

## 19 komend slash

```
Budowa i rozwój:     /botforge-new /botforge-extend /botforge-review /botforge-refactor
Moduły:              /botforge-miniapp /botforge-auth /botforge-payments
                     /botforge-broadcast /botforge-admin /botforge-admin-web
                     /botforge-scheduler /botforge-inline /botforge-i18n
Operacje:            /botforge-test /botforge-deploy /botforge-security
                     /botforge-botfather /botforge-observability /botforge-help
```

## Działający przykład

[`examples/01-vip-media-bot/`](../../examples/01-vip-media-bot/) — bot VIP na Telegram Stars, 25 plików Python, wszystko zgodnie ze standardem skilla.

```bash
cd examples/01-vip-media-bot
cp .env.example .env   # ustaw BOT_TOKEN, ADMIN_IDS
make up
```

## Cztery tryby

| Tryb | Kiedy | Różnice |
|---|---|---|
| **Lite** | MVP w jeden wieczór | SQLite, polling, bez Dockera |
| **Pro** (domyślny) | Bot komercyjny | Pełny standard produkcyjny |
| **Media** | Treści / kanały | + synchronizacja CMS, broadcasty z segmentacją, UTM |
| **SaaS** | Subskrypcje / VIP | + billing, wielu providerów płatności, metryki admina |

## Zawartość

| Plik | Przeznaczenie |
|---|---|
| [`SKILL.md`](../../SKILL.md) | Pełny dokument skilla — manifest, system prompt, reguły, wzorce |
| [`system_prompt.txt`](../../system_prompt.txt) | Surowy system prompt dla dowolnego LLM |
| [`.claude/skills/botforge/`](../../.claude/skills/botforge/) | **Claude Code** Agent Skill z 23 referencjami |
| [`.claude/commands/`](../../.claude/commands/) | 19 komend slash |
| [`.claude-plugin/plugin.json`](../../.claude-plugin/plugin.json) | Manifest pluginu |
| [`cursor/.cursor/rules/botforge.mdc`](../../cursor/.cursor/rules/botforge.mdc) | Reguły **Cursora** (nowoczesne MDC) |
| [`codex/AGENTS.md`](../../codex/AGENTS.md) | **Codex / Aider / Continue** |
| [`.vscode/`](../../.vscode/) | Snippety VS Code (`bf-new`, `bf-extend`, …) |
| [`.zed/`](../../.zed/) | Konfiguracja Zed |
| [`tests/golden/`](../../tests/golden/) | Eval harness: strukturalne asercje na output AI |
| [`examples/`](../../examples/) | Działające przykłady botów |

## Dokumentacja

- [QUICKSTART](../QUICKSTART.md) — 5 minut od zera do bota
- [INSTALL](../INSTALL.md) — szczegółowa konfiguracja dla każdego narzędzia
- [USAGE](../USAGE.md) — tryby, formaty promptów, cykl sesji
- [COMPARISON](../COMPARISON.md) — vs zwykłe prompty, cookiecutter, no-code, generic agents
- [SHOWCASE](../SHOWCASE.md) — boty zbudowane z BotForge
- [CHANGELOG](../CHANGELOG.md) — historia wersji i roadmap

## Biblioteka referencji

23 szczegółowe dokumenty obejmujące wszystkie aspekty inżynierii botów Telegrama: architekturę, 12 wzorców wielokrotnego użytku, Mini Apps, auth (role / initData / OAuth / API keys), płatności (5 providerów), oficjalne ograniczenia Bot API 9.6, setup BotFather, i18n, obserwowalność, zadania cykliczne, subskrypcje recurring, tryb inline, grupy/kanały/fora, obsługa mediów, anti-spam, zgodność z GDPR, analytics, anty-wzorce, performance, panel admina, FAQ.

## Licencja

MIT. Korzystaj swobodnie w projektach komercyjnych.

## Współtworzenie

Zobacz [CONTRIBUTING](../../CONTRIBUTING.md) i [SECURITY](../../SECURITY.md). Pull requesty mile widziane.
