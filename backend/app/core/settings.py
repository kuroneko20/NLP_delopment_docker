from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Banking AI-Agent API Gateway"
    app_version: str = "1.0.0"
    intent_service_host: str = Field(default="intent-service", alias="INTENT_SERVICE_HOST")
    intent_service_port: int = Field(default=50051, alias="INTENT_SERVICE_PORT")
    ollama_base_url: str = Field(default="http://host.docker.internal:11434", alias="OLLAMA_BASE_URL")
    intent_model_name: str = Field(default="gpt-oss:20b", alias="INTENT_MODEL_NAME")
    grpc_timeout_seconds: float = Field(default=5.0, alias="GRPC_TIMEOUT_SECONDS")
    http_timeout_seconds: float = Field(default=30.0, alias="HTTP_TIMEOUT_SECONDS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def intent_service_target(self) -> str:
        return f"{self.intent_service_host}:{self.intent_service_port}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
