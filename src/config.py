"""
config.py — Configurações e variáveis de ambiente da aplicação.

Carrega as configurações a partir de variáveis de ambiente (arquivo .env em
desenvolvimento). Em produção, as variáveis devem ser configuradas diretamente
no painel do provedor de nuvem (ex: Render).
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações centralizadas da aplicação (lidas do .env ou do ambiente)."""

    # Autenticação
    api_key: str = Field(..., description="Chave de API para autenticar requisições")

    # Solver
    solver_default_time_limit: int = Field(
        default=60,
        ge=1,
        le=120,
        description="Tempo padrão (segundos) para o solver OR-Tools",
    )
    solver_max_time_limit: int = Field(
        default=120,
        ge=1,
        description="Limite máximo aceito de time_limit enviado pelo cliente",
    )

    # Aplicação
    app_name: str = Field(
        default="Optimization-as-a-Service — Corte Unidimensional",
        description="Nome da aplicação exibido no Swagger",
    )
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(
        default=False,
        description="Se True, exibe tracebacks detalhados (somente desenvolvimento)",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retorna as configurações em cache (instanciadas uma única vez)."""
    return Settings()


# Instância global conveniente para importação direta
settings = get_settings()
