from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-sonnet-4-20250514"

    # Evolution API
    evolution_api_url: str = "http://evolution-api:8080"
    evolution_api_key: str = ""
    evolution_instance_name: str = "intelecto"

    # App
    log_level: str = "info"
    soul_path: str = "soul.md"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
