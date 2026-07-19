from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = APP_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    service_name: str = "pokeauthai-backend"
    version: str = "1.0.0"
    cors_origins: str = "http://localhost:3000"
    
    pokemon_tcg_api_base_url: str = "https://api.pokemontcg.io/v2"
    pokemon_tcg_api_timeout_seconds: float = 15.0
    pokemon_tcg_api_key: str | None = None
    
    cardmarket_api_key: str | None = None
    
    cache_ttl: int = 86400  # 1 day default
    log_level: str = "INFO"
    
    ml_model_enabled: bool = False
    ml_model_path: str = str(
        APP_ROOT / "ml_models" / "best_model.onnx"
    )
    ml_model_format: str = "onnx"
    ml_counterfeit_threshold: float = 0.5
    ml_uncertainty_margin: float = 0.15

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
