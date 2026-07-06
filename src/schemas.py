"""
schemas.py — Validadores Pydantic de entrada e saída da API de Otimização.

Define os contratos JSON documentados em specs/0001-api-otimizacao/spec.md.
Todos os campos usam a linguagem ubíqua definida em specs/0001-api-otimizacao/domain.md.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Modelos de ENTRADA
# ---------------------------------------------------------------------------


class Item(BaseModel):
    """Um item de demanda com comprimento e quantidade solicitada.

    Cobre: AC-3, AC-4, AC-5.
    """

    id: str = Field(
        ...,
        description="Identificador único do item de demanda",
        examples=["item_A"],
    )
    comprimento: int = Field(
        ...,
        gt=0,
        description="Comprimento necessário do item em milímetros (deve ser > 0)",
        examples=[1150],
    )
    quantidade: int = Field(
        ...,
        gt=0,
        description="Quantidade demandada do item (deve ser > 0)",
        examples=[3],
    )


class OptimizationRequest(BaseModel):
    """Payload de entrada para a rota POST /otimizar.

    Cobre: AC-2, AC-3, AC-4, AC-5, AC-10.
    """

    comprimento_padrao: int = Field(
        ...,
        gt=0,
        description=(
            "Comprimento útil de cada barra padrão em estoque (em milímetros). "
            "Deve ser estritamente positivo."
        ),
        examples=[3000],
    )
    itens: List[Item] = Field(
        ...,
        min_length=1,
        description="Lista de itens de demanda a serem cortados. Deve ter pelo menos 1 item.",
        examples=[
            [
                {"id": "item_A", "comprimento": 1150, "quantidade": 3},
                {"id": "item_B", "comprimento": 800, "quantidade": 4},
                {"id": "item_C", "comprimento": 450, "quantidade": 5},
            ]
        ],
    )
    time_limit: Optional[int] = Field(
        default=None,
        ge=1,
        le=120,
        description=(
            "Tempo máximo (em segundos) para o solver buscar a solução. "
            "Mínimo: 1s. Máximo: 120s. Padrão: 60s."
        ),
        examples=[60],
    )

    @model_validator(mode="after")
    def validar_comprimentos_dos_itens(self) -> "OptimizationRequest":
        """Garante que nenhum item tenha comprimento maior que o comprimento padrão.

        Cobre: AC-4.
        """
        for item in self.itens:
            if item.comprimento > self.comprimento_padrao:
                raise ValueError(
                    f"O item '{item.id}' tem comprimento {item.comprimento} mm, "
                    f"que excede o comprimento padrão da barra ({self.comprimento_padrao} mm). "
                    "Nenhum item pode ser maior que a barra padrão."
                )
        return self


# ---------------------------------------------------------------------------
# Modelos de SAÍDA
# ---------------------------------------------------------------------------


class ItemCortado(BaseModel):
    """Representa a quantidade de um item cortado em uma barra específica."""

    item_id: str = Field(..., description="Identificador do item de demanda cortado")
    quantidade: int = Field(..., description="Quantidade do item cortada nesta barra")


class BarraCorte(BaseModel):
    """Especificação de corte de uma única barra padrão."""

    barra_id: int = Field(..., description="Identificador sequencial da barra (começa em 1)")
    itens_cortados: List[ItemCortado] = Field(
        ..., description="Lista de itens e quantidades extraídas desta barra"
    )
    comprimento_utilizado: int = Field(
        ..., description="Soma dos comprimentos efetivamente cortados nesta barra (mm)"
    )
    sobra: int = Field(
        ..., description="Comprimento remanescente não utilizado nesta barra (mm)"
    )


class OptimizationResponse(BaseModel):
    """Resposta da rota POST /otimizar contendo o plano de corte.

    Cobre: AC-2.
    """

    status_solver: str = Field(
        ...,
        description="Resultado do processo de otimização: OPTIMAL, FEASIBLE ou INFEASIBLE",
        examples=["OPTIMAL"],
    )
    tempo_execucao_segundos: float = Field(
        ...,
        description="Tempo real gasto pelo solver para encontrar a solução (em segundos)",
        examples=[0.045],
    )
    barras_utilizadas: int = Field(
        ...,
        description="Número total de barras padrão utilizadas no plano de corte",
        examples=[4],
    )
    desperdicio_total_mm: int = Field(
        ...,
        description="Soma das sobras de todas as barras utilizadas (em mm)",
        examples=[3100],
    )
    plano_corte: List[BarraCorte] = Field(
        ...,
        description="Especificação detalhada dos cortes para cada barra utilizada",
    )


# ---------------------------------------------------------------------------
# Modelos de ERRO e HEALTH
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    """Resposta do endpoint GET /health."""

    status: str = Field(default="ok", examples=["ok"])


class ErrorResponse(BaseModel):
    """Resposta genérica de erro (sem traceback exposto). Cobre: AC-12."""

    detail: str = Field(..., description="Mensagem de erro legível pelo cliente")
