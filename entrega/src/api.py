"""
api.py — Configuração do FastAPI e endpoints da API de Otimização.

Expõe:
  GET  /health    — Liveness probe
  POST /otimizar  — Solve do corte unidimensional

Proteção de traceback em produção.
"""

import logging
import traceback

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.auth import verify_api_key
from src.config import get_settings
from src.schemas import (
    ErrorResponse,
    HealthResponse,
    OptimizationRequest,
    OptimizationResponse,
)
from src.solver import resolver_corte

# ---------------------------------------------------------------------------
# Logger da aplicação
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Instância do FastAPI com metadados para Swagger
# ---------------------------------------------------------------------------
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API REST para resolução do **Problema de Corte Unidimensional** (1D Cutting Stock Problem) "
        "usando Google OR-Tools com a formulação de Kantorovich.\n\n"
        "## Autenticação\n"
        "Todos os endpoints protegidos requerem o cabeçalho `X-API-Key` com a chave correta.\n\n"
        "## Confiabilidade\n"
        "O parâmetro `time_limit` (1–120s, padrão 60s) garante que o solver sempre retorne "
        "dentro do tempo especificado, mesmo que com uma solução `FEASIBLE` em vez de `OPTIMAL`."
    ),
    contact={
        "name": "Laboratório de Otimização — UFC Ciências de Dados",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {"name": "saúde", "description": "Verificação de disponibilidade da API"},
        {
            "name": "otimização",
            "description": "Resolução do Problema de Corte Unidimensional",
        },
    ],
)

# ---------------------------------------------------------------------------
# CORS — permite acesso do Swagger UI e de clientes externos
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Handler global de erros — garante que tracebacks não vazem
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Captura qualquer exceção não tratada e oculta o traceback em produção."""
    logger.error(
        "Erro interno não tratado em %s: %s\n%s",
        request.url,
        exc,
        traceback.format_exc(),
    )

    if settings.debug:
        # Em desenvolvimento: expõe o traceback completo
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": traceback.format_exc()},
        )

    # Em produção: mensagem genérica sem traceback
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor. Tente novamente mais tarde."},
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get(
    "/health",
    tags=["saúde"],
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Verifica se a API está online e respondendo normalmente.",
    responses={200: {"description": "API online e operacional"}},
)
async def health_check() -> HealthResponse:
    """
    Retorna `{"status": "ok"}` se a API estiver operando normalmente.
    """
    return HealthResponse(status="ok")


@app.post(
    "/otimizar",
    tags=["otimização"],
    response_model=OptimizationResponse,
    summary="Resolver o Problema de Corte Unidimensional",
    description=(
        "Recebe o comprimento padrão da barra e a lista de itens de demanda, "
        "e retorna o plano de corte ótimo (ou melhor factível) minimizando o número "
        "de barras utilizadas.\n\n"
        "**Autenticação obrigatória:** envie o cabeçalho `X-API-Key` com sua chave."
    ),
    responses={
        200: {"description": "Plano de corte calculado com sucesso"},
        403: {
            "model": ErrorResponse,
            "description": "API Key ausente ou inválida",
        },
        422: {
            "description": "Parâmetros de entrada inválidos (validação Pydantic)",
        },
        500: {
            "model": ErrorResponse,
            "description": "Erro interno do servidor",
        },
    },
)
async def otimizar(
    request: OptimizationRequest,
    _api_key: str = Depends(verify_api_key),
) -> OptimizationResponse:
    """
    Resolve o problema de corte unidimensional via OR-Tools.
    """
    # Determina o time_limit efetivo
    time_limit = request.time_limit if request.time_limit is not None else settings.solver_default_time_limit

    logger.info(
        "Nova requisição de otimização: comprimento_padrao=%d, n_itens=%d, time_limit=%ds",
        request.comprimento_padrao,
        len(request.itens),
        time_limit,
    )

    resultado = resolver_corte(
        comprimento_padrao=request.comprimento_padrao,
        itens=request.itens,
        time_limit_seconds=time_limit,
    )

    logger.info(
        "Otimização concluída: status=%s, barras=%d, tempo=%.3fs",
        resultado.status_solver,
        resultado.barras_utilizadas,
        resultado.tempo_execucao_segundos,
    )

    return resultado
