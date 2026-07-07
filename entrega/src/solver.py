"""
solver.py — Modelagem matemática do Problema de Corte Unidimensional com OR-Tools.

Implementa a formulação de Kantorovich (MIP) conforme ADR-0003 e o modelo
definido em specs/0001-api-otimizacao/domain.md.

Formulação:
    Minimizar:  Z = Σ_j y_j
    Sujeito a:  Σ_j x_ij >= d_i,  para todo i  (demanda atendida)
                Σ_i l_i * x_ij <= L * y_j, para todo j  (capacidade da barra)
                y_j ∈ {0,1},  x_ij ∈ Z>=0

Onde:
    L   = comprimento padrão da barra
    l_i = comprimento do item i
    d_i = demanda do item i
    N   = Σ d_i  (upper bound do número de barras)

"""

import time
from dataclasses import dataclass, field
from typing import Dict, List

from ortools.sat.python import cp_model

from src.schemas import BarraCorte, Item, ItemCortado, OptimizationResponse


# ---------------------------------------------------------------------------
# Mapeamento dos status do OR-Tools → termos do domínio
# ---------------------------------------------------------------------------
_STATUS_MAP: Dict[int, str] = {
    cp_model.OPTIMAL: "OPTIMAL",
    cp_model.FEASIBLE: "FEASIBLE",
    cp_model.INFEASIBLE: "INFEASIBLE",
    cp_model.MODEL_INVALID: "INFEASIBLE",
    cp_model.UNKNOWN: "INFEASIBLE",
}


@dataclass
class SolverInput:
    """Dados de entrada já validados para o solver."""

    comprimento_padrao: int
    itens: List[Item]
    time_limit_seconds: int


@dataclass
class SolverOutput:
    """Saída bruta do solver antes de serializar para o schema de resposta."""

    status: str
    elapsed_seconds: float
    barras_utilizadas: int = 0
    desperdicio_total_mm: int = 0
    plano: List[BarraCorte] = field(default_factory=list)


def resolver_corte(
    comprimento_padrao: int,
    itens: List[Item],
    time_limit_seconds: int = 60,
) -> OptimizationResponse:
    """Resolve o Problema de Corte Unidimensional usando OR-Tools (CP-SAT).

    Args:
        comprimento_padrao: Comprimento útil de cada barra padrão (mm).
        itens: Lista de itens de demanda com comprimento e quantidade.
        time_limit_seconds: Limite de tempo do solver em segundos (1–120).

    Returns:
        OptimizationResponse com o plano de corte completo.

    """
    inicio = time.perf_counter()

    # Upper bound: no pior caso, uma barra por unidade de demanda
    n_barras_max = sum(item.quantidade for item in itens)
    n_itens = len(itens)

    model = cp_model.CpModel()

    # ---------------------------------------------------------------------------
    # Variáveis de decisão
    # ---------------------------------------------------------------------------
    # y[j] = 1 se a barra j é utilizada
    y = [model.new_bool_var(f"y_{j}") for j in range(n_barras_max)]

    # x[i][j] = quantidade do item i cortada da barra j
    x = [
        [
            model.new_int_var(0, itens[i].quantidade, f"x_{i}_{j}")
            for j in range(n_barras_max)
        ]
        for i in range(n_itens)
    ]

    # ---------------------------------------------------------------------------
    # Restrições
    # ---------------------------------------------------------------------------
    # (2) Demanda de cada item deve ser atendida
    for i in range(n_itens):
        model.add(sum(x[i][j] for j in range(n_barras_max)) >= itens[i].quantidade)

    # (3) Comprimento total de cada barra não pode exceder L * y_j
    for j in range(n_barras_max):
        model.add(
            sum(itens[i].comprimento * x[i][j] for i in range(n_itens))
            <= comprimento_padrao * y[j]
        )

    # Simetria: se barra j não é usada (y[j]=0), todos os x[i][j] devem ser 0
    # (já garantido pela restrição (3), mas adicionar reduz o espaço de busca)
    for j in range(n_barras_max):
        for i in range(n_itens):
            model.add(x[i][j] <= itens[i].quantidade * y[j])

    # Quebra de simetria: forçar a ordem de uso das barras (barra j só usada se j-1 usada)
    for j in range(1, n_barras_max):
        model.add(y[j] <= y[j - 1])

    # ---------------------------------------------------------------------------
    # Função objetivo: minimizar número de barras usadas
    # ---------------------------------------------------------------------------
    model.minimize(sum(y))

    # ---------------------------------------------------------------------------
    # Solver e configuração
    # ---------------------------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit_seconds)
    solver.parameters.num_search_workers = 1  # Determinístico para testes

    status_code = solver.solve(model)
    elapsed = time.perf_counter() - inicio

    status_str = _STATUS_MAP.get(status_code, "INFEASIBLE")

    # ---------------------------------------------------------------------------
    # Construção da resposta
    # ---------------------------------------------------------------------------
    if status_str == "INFEASIBLE":
        return OptimizationResponse(
            status_solver="INFEASIBLE",
            tempo_execucao_segundos=round(elapsed, 6),
            barras_utilizadas=0,
            desperdicio_total_mm=0,
            plano_corte=[],
        )

    plano_corte: List[BarraCorte] = []
    total_desperdicio = 0
    barra_counter = 1

    for j in range(n_barras_max):
        if solver.value(y[j]) == 1:
            itens_cortados: List[ItemCortado] = []
            comprimento_usado = 0

            for i in range(n_itens):
                qtd = solver.value(x[i][j])
                if qtd > 0:
                    itens_cortados.append(
                        ItemCortado(item_id=itens[i].id, quantidade=qtd)
                    )
                    comprimento_usado += itens[i].comprimento * qtd

            sobra = comprimento_padrao - comprimento_usado
            total_desperdicio += sobra

            plano_corte.append(
                BarraCorte(
                    barra_id=barra_counter,
                    itens_cortados=itens_cortados,
                    comprimento_utilizado=comprimento_usado,
                    sobra=sobra,
                )
            )
            barra_counter += 1

    return OptimizationResponse(
        status_solver=status_str,
        tempo_execucao_segundos=round(elapsed, 6),
        barras_utilizadas=len(plano_corte),
        desperdicio_total_mm=total_desperdicio,
        plano_corte=plano_corte,
    )
