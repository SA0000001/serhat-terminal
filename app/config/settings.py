"""Configuration loading from environment + YAML."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    env: str = "dev"
    app_name: str = "Trading Research Platform"
    database_url: str = "sqlite+pysqlite:///./local.db"
    redis_url: str = "redis://localhost:6379/0"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    ai_provider: str = "mock"
    ai_model: str = "gpt-4o-mini"
    config_path: str = "config/settings.yaml"
    api_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class YamlConfig(BaseModel):
    research: dict[str, Any]
    trading: dict[str, Any]
    dashboard: dict[str, Any]


def load_yaml_config(path: str) -> YamlConfig:
    config_path = Path(path)
    payload = yaml.safe_load(config_path.read_text())
    return YamlConfig.model_validate(payload)
