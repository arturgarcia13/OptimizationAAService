"""
test_solver.py — Testes unitários do modelo matemático (solver OR-Tools).

Cada teste mapeia para ACs da spec: specs/0001-api-otimizacao/spec.md
Gate: pytest tests/test_solver.py -v
"""

import pytest

from src.schemas import Item, OptimizationRequest
from src.solver import resolver_corte


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fazer_item(id_: str, comprimento: int, quantidade: int) -> Item:
    return Item(id=id_, comprimento=comprimento, quantidade=quantidade)


# ---------------------------------------------------------------------------
# Testes do solver (test_solver.py)
# ---------------------------------------------------------------------------


class TestSolverOtimizacaoBasica:
    """Testes das propriedades da solução ótima."""

    def test_instancia_trivial_uma_barra_exata(self):
        """Uma barra de 1000mm, 1 item de 1000mm x1 → 1 barra, 0 de desperdício."""
        itens = [_fazer_item("A", 1000, 1)]
        resultado = resolver_corte(1000, itens, time_limit_seconds=30)

        assert resultado.status_solver in ("OPTIMAL", "FEASIBLE")
        assert resultado.barras_utilizadas == 1
        assert resultado.desperdicio_total_mm == 0
        assert len(resultado.plano_corte) == 1
        assert resultado.plano_corte[0].sobra == 0

    def test_instancia_dois_itens_cabem_em_uma_barra(self):
        """Dois itens que somam exatamente o comprimento da barra → 1 barra."""
        itens = [
            _fazer_item("A", 600, 1),
            _fazer_item("B", 400, 1),
        ]
        resultado = resolver_corte(1000, itens, time_limit_seconds=30)

        assert resultado.status_solver in ("OPTIMAL", "FEASIBLE")
        assert resultado.barras_utilizadas == 1
        assert resultado.desperdicio_total_mm == 0

    def test_instancia_classica_do_enunciado(self):
        """Instância do projeto_final.md: barra=3000, 3 tipos de itens.

        status OPTIMAL, barras > 0, desperdício >= 0, plano não vazio.
        """
        itens = [
            _fazer_item("item_A", 1150, 3),
            _fazer_item("item_B", 800, 4),
            _fazer_item("item_C", 450, 5),
        ]
        resultado = resolver_corte(3000, itens, time_limit_seconds=60)

        assert resultado.status_solver in ("OPTIMAL", "FEASIBLE")
        assert resultado.barras_utilizadas > 0
        assert resultado.desperdicio_total_mm >= 0
        assert len(resultado.plano_corte) == resultado.barras_utilizadas

        # Verifica invariante: comprimento_utilizado + sobra == comprimento_padrao
        for barra in resultado.plano_corte:
            assert barra.comprimento_utilizado + barra.sobra == 3000

    def test_invariante_demanda_suprida(self):
        """Verifica que a demanda de cada item é completamente atendida no plano."""
        itens = [
            _fazer_item("item_A", 1150, 3),
            _fazer_item("item_B", 800, 4),
            _fazer_item("item_C", 450, 5),
        ]
        resultado = resolver_corte(3000, itens, time_limit_seconds=60)

        # Conta quanto foi cortado de cada item
        cortado_por_item: dict[str, int] = {}
        for barra in resultado.plano_corte:
            for item_cortado in barra.itens_cortados:
                cortado_por_item[item_cortado.item_id] = (
                    cortado_por_item.get(item_cortado.item_id, 0) + item_cortado.quantidade
                )

        for item in itens:
            assert cortado_por_item.get(item.id, 0) >= item.quantidade, (
                f"Demanda do item '{item.id}' não foi totalmente atendida"
            )

    def test_desperdicio_total_correto(self):
        """Desperdicio total deve ser a soma das sobras de todas as barras."""
        itens = [
            _fazer_item("X", 700, 2),
            _fazer_item("Y", 400, 3),
        ]
        resultado = resolver_corte(1000, itens, time_limit_seconds=30)

        soma_sobras = sum(b.sobra for b in resultado.plano_corte)
        assert resultado.desperdicio_total_mm == soma_sobras

    def test_solver_respeita_time_limit_pequeno(self):
        """Com time_limit=1s, o solver retorna OPTIMAL ou FEASIBLE sem travar."""
        itens = [
            _fazer_item("A", 100, 5),
            _fazer_item("B", 200, 3),
        ]
        resultado = resolver_corte(500, itens, time_limit_seconds=1)

        assert resultado.status_solver in ("OPTIMAL", "FEASIBLE", "INFEASIBLE")
        # Tempo de execução deve ser próximo ao limite (não ultrapassar muito)
        assert resultado.tempo_execucao_segundos < 10  # margem generosa


class TestSolverValidacaoSchemas:
    """Testes das validações Pydantic do schema de entrada."""

    def test_comprimento_padrao_zero_invalido(self):
        """comprimento_padrao=0 deve levantar ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            OptimizationRequest(
                comprimento_padrao=0,
                itens=[{"id": "A", "comprimento": 100, "quantidade": 1}],
            )
        assert "comprimento_padrao" in str(exc_info.value)

    def test_comprimento_padrao_negativo_invalido(self):
        """comprimento_padrao negativo deve levantar ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OptimizationRequest(
                comprimento_padrao=-500,
                itens=[{"id": "A", "comprimento": 100, "quantidade": 1}],
            )

    def test_item_comprimento_maior_que_barra_invalido(self):
        """Item com comprimento > comprimento_padrao deve ser rejeitado."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            OptimizationRequest(
                comprimento_padrao=1000,
                itens=[{"id": "grande", "comprimento": 1500, "quantidade": 1}],
            )
        assert "grande" in str(exc_info.value) or "excede" in str(exc_info.value)

    def test_quantidade_zero_invalida(self):
        """quantidade=0 deve levantar ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OptimizationRequest(
                comprimento_padrao=1000,
                itens=[{"id": "A", "comprimento": 500, "quantidade": 0}],
            )

    def test_quantidade_negativa_invalida(self):
        """quantidade negativa deve levantar ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OptimizationRequest(
                comprimento_padrao=1000,
                itens=[{"id": "A", "comprimento": 500, "quantidade": -2}],
            )

    def test_time_limit_acima_maximo_invalido(self):
        """time_limit > 120 deve levantar ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OptimizationRequest(
                comprimento_padrao=1000,
                itens=[{"id": "A", "comprimento": 500, "quantidade": 1}],
                time_limit=200,
            )

    def test_time_limit_zero_invalido(self):
        """time_limit=0 deve levantar ValidationError."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OptimizationRequest(
                comprimento_padrao=1000,
                itens=[{"id": "A", "comprimento": 500, "quantidade": 1}],
                time_limit=0,
            )

    def test_time_limit_maximo_valido(self):
        """time_limit=120 é o limite superior e deve ser aceito."""
        req = OptimizationRequest(
            comprimento_padrao=1000,
            itens=[{"id": "A", "comprimento": 500, "quantidade": 1}],
            time_limit=120,
        )
        assert req.time_limit == 120

    def test_lista_itens_vazia_invalida(self):
        """Lista de itens vazia deve ser rejeitada."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OptimizationRequest(comprimento_padrao=1000, itens=[])

    def test_item_comprimento_igual_barra_valido(self):
        """Item com comprimento == comprimento_padrao é válido (sobra zero)."""
        req = OptimizationRequest(
            comprimento_padrao=1000,
            itens=[{"id": "A", "comprimento": 1000, "quantidade": 2}],
        )
        resultado = resolver_corte(
            req.comprimento_padrao, req.itens, time_limit_seconds=10
        )
        assert resultado.barras_utilizadas == 2
        for barra in resultado.plano_corte:
            assert barra.sobra == 0
