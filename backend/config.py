from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    api_title: str = "Lab Suite API"
    api_description: str = "Microservicio para Lab Suite, extension de productividad"
    api_version: str = "1.0.0"
    environment: str = "development"

    frontend_url: str = "http://localhost:3000"
    github_pages_url: str = "https://evar-7.github.io/lab-suite"
    cors_origins: str = ""

    database_url: str = "sqlite:///./lab_suite.db"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @property
    def allowed_origins(self) -> List[str]:
        production_env = self.environment.lower() == "production"

        base_origins = [self.frontend_url, self.github_pages_url]
        if not production_env:
            base_origins.extend(
                [
                    "http://localhost:3000",
                    "http://localhost:8080",
                    "http://localhost:8000",
                    "https://localhost:3000",
                    "https://localhost:8080",
                ]
            )

        if self.cors_origins.strip():
            base_origins.extend(
                origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
            )

        deduped: List[str] = []
        for origin in base_origins:
            normalized = origin.strip().rstrip("/")
            if normalized and normalized not in deduped:
                deduped.append(normalized)
        return deduped


@lru_cache
def get_settings() -> Settings:
    return Settings()


