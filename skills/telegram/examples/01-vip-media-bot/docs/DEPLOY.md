# Deploy

## VPS + Docker Compose

```bash
# на сервере:
git clone https://github.com/<you>/vip-media-bot.git
cd vip-media-bot
cp .env.example .env
nano .env          # заполнить BOT_TOKEN, ADMIN_IDS, REQUIRED_CHANNELS, WEBHOOK_URL
docker compose up -d
docker compose logs -f bot
```

Настройте nginx / Caddy для TLS на `WEBHOOK_URL` → `127.0.0.1:8080`.

### Caddyfile пример
```
bot.example.com {
  reverse_proxy 127.0.0.1:8080
}
```

## Fly.io

```bash
fly launch --no-deploy
fly postgres create
fly postgres attach <cluster>
fly redis create
fly secrets set BOT_TOKEN=... ADMIN_IDS='[123]' REQUIRED_CHANNELS='[]' \
                WEBHOOK_URL=https://<app>.fly.dev WEBHOOK_SECRET=$(openssl rand -hex 32)
fly deploy
```

## Railway

1. Create new project → Deploy from GitHub
2. Add Postgres + Redis plugins
3. Set env vars via dashboard
4. `WEBHOOK_URL` = `https://<service>-<project>.up.railway.app`

## Verification

```bash
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo" | jq
# ожидание: last_error_date == null, url == ваш webhook URL
```

Отправьте `/start` — бот должен ответить.

## Rollback

```bash
docker compose pull bot
docker compose up -d bot    # downgrade к previous image
# Alembic:
docker compose exec bot alembic downgrade -1
```
