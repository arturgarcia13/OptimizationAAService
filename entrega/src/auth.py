"""
auth.py — Lógica de controle de acesso via API Key.

Implementa a Opção A (API Key) conforme ADR-0002. A chave é comparada contra
o valor em settings.api_key (variável de ambiente API_KEY).

"""

from fastapi import HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from src.config import get_settings

# Define o esquema de segurança que o Swagger UI usará para autenticação
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,  # Tratamos o erro manualmente para retornar 403 (não 422)
    description="Chave de API necessária para acessar os endpoints protegidos",
)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """Dependency do FastAPI que valida o cabeçalho X-API-Key.

    Retorna a chave validada se correta, ou levanta HTTPException 403 se
    ausente ou incorreta.

    """
    settings = get_settings()

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: cabeçalho X-API-Key ausente.",
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: API Key inválida.",
        )

    return api_key
