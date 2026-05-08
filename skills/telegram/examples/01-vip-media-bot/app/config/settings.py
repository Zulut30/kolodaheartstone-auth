from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str
    admin_ids: list[int] = []
    required_channels: list[int] = []

    database_url: str
    redis_url: str = "redis://redis:6379/0"

    webhook_url: str | None = None
    webhook_secret: str | None = None
    webhook_path: str = "/tg/webhook"
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8080

    log_level: str = "INFO"
    sentry_dsn: str | None = None

    vip_price_stars: int = 100
    vip_duration_days: int = 30


settings = Settings()
