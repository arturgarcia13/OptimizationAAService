"""
test_api.py — Testes de integração das rotas da API (FastAPI + httpx).

Usa TestClient do FastAPI para testar os endpoints reais com autenticação,
validação e comportamento completo de ponta-a-ponta.

Gate: pytest tests/test_api.py -v
"""

import os

import pytest
from fastapi.testclient import TestClient

# Garante que a variável de ambiente API_KEY esteja disponível antes de importar a app
os.environ.setdefault("API_KEY", "test-api-key-segura-12345")

from src.api import app  # noqa: E402 — importação após setenv é intencional

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_API_KEY = "test-api-key-segura-12345"
INVALID_API_KEY = "chave-errada"

PAYLOAD_VALIDO = {
    "comprimento_padrao": 3000,
    "itens": [
        {"id": "item_A", "comprimento": 1150, "quantidade": 3},
        {"id": "item_B", "comprimento": 800, "quantidade": 4},
        {"id": "item_C", "comprimento": 450, "quantidade": 5},
    ],
}


@pytest.fixture(scope="module")
def client():
    """TestClient reutilizado por todos os testes do módulo."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def headers_validos():
    """Cabeçalho com API Key válida."""
    return {"X-API-Key": VALID_API_KEY}


# ---------------------------------------------------------------------------
# Testes de saúde (AC-1, AC-11)
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    """Testes do endpoint GET /health. Cobre: AC-1."""

    def test_health_retorna_200(self, client: TestClient):
        """GET /health deve retornar 200. Cobre: AC-1."""
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_retorna_status_ok(self, client: TestClient):
        """GET /health deve retornar {'status': 'ok'}. Cobre: AC-1."""
        resp = client.get("/health")
        assert resp.json() == {"status": "ok"}

    def test_swagger_docs_acessivel(self, client: TestClient):
        """GET /docs deve retornar 200. Cobre: AC-11."""
        resp = client.get("/docs")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Testes de segurança (AC-6, AC-7)
# ---------------------------------------------------------------------------


class TestAutenticacao:
    """Testes de autenticação da rota POST /otimizar. Cobre: AC-6, AC-7."""

    def test_sem_api_key_retorna_403(self, client: TestClient):
        """POST /otimizar sem X-API-Key deve retornar 403. Cobre: AC-6."""
        resp = client.post("/otimizar", json=PAYLOAD_VALIDO)
        assert resp.status_code == 403

    def test_api_key_invalida_retorna_403(self, client: TestClient):
        """POST /otimizar com X-API-Key errada deve retornar 403. Cobre: AC-7."""
        resp = client.post(
            "/otimizar",
            json=PAYLOAD_VALIDO,
            headers={"X-API-Key": INVALID_API_KEY},
        )
        assert resp.status_code == 403

    def test_403_sem_traceback_exposto(self, client: TestClient):
        """Resposta 403 não deve expor informações internas. Cobre: AC-12."""
        resp = client.post("/otimizar", json=PAYLOAD_VALIDO)
        body = resp.json()
        assert "detail" in body
        # Não deve conter termos típicos de tracebacks Python
        assert "Traceback" not in body["detail"]
        assert "File " not in body["detail"]


# ---------------------------------------------------------------------------
# Testes de validação Pydantic (AC-3, AC-4, AC-5, AC-10)
# ---------------------------------------------------------------------------


class TestValidacaoEntrada:
    """Testes de validação de parâmetros de entrada. Cobre: AC-3, AC-4, AC-5, AC-10."""

    def test_comprimento_padrao_zero_retorna_422(
        self, client: TestClient, headers_validos: dict
    ):
        """comprimento_padrao=0 deve retornar 422. Cobre: AC-3."""
        payload = {**PAYLOAD_VALIDO, "comprimento_padrao": 0}
        resp = client.post("/otimizar", json=payload, headers=headers_validos)
        assert resp.status_code == 422

    def test_item_comprimento_maior_que_barra_retorna_422(
        self, client: TestClient, headers_validos: dict
    ):
        """Item maior que a barra deve retornar 422. Cobre: AC-4."""
        payload = {
            "comprimento_padrao": 1000,
            "itens": [{"id": "big", "comprimento": 1500, "quantidade": 1}],
        }
        resp = client.post("/otimizar", json=payload, headers=headers_validos)
        assert resp.status_code == 422

    def test_quantidade_zero_retorna_422(
        self, client: TestClient, headers_validos: dict
    ):
        """quantidade=0 deve retornar 422. Cobre: AC-5."""
        payload = {
            "comprimento_padrao": 1000,
            "itens": [{"id": "A", "comprimento": 500, "quantidade": 0}],
        }
        resp = client.post("/otimizar", json=payload, headers=headers_validos)
        assert resp.status_code == 422

    def test_time_limit_acima_120_retorna_422(
        self, client: TestClient, headers_validos: dict
    ):
        """time_limit=200 deve retornar 422. Cobre: AC-10."""
        payload = {**PAYLOAD_VALIDO, "time_limit": 200}
        resp = client.post("/otimizar", json=payload, headers=headers_validos)
        assert resp.status_code == 422

    def test_lista_itens_vazia_retorna_422(
        self, client: TestClient, headers_validos: dict
    ):
        """Lista de itens vazia deve retornar 422."""
        payload = {"comprimento_padrao": 1000, "itens": []}
        resp = client.post("/otimizar", json=payload, headers=headers_validos)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Testes de otimização — happy path (AC-2, AC-8, AC-9)
# ---------------------------------------------------------------------------


class TestOtimizacao:
    """Testes do fluxo principal de otimização. Cobre: AC-2, AC-8, AC-9."""

    def test_payload_valido_retorna_200(
        self, client: TestClient, headers_validos: dict
    ):
        """POST /otimizar com payload válido deve retornar 200. Cobre: AC-2."""
        resp = client.post("/otimizar", json=PAYLOAD_VALIDO, headers=headers_validos)
        assert resp.status_code == 200

    def test_resposta_tem_campos_obrigatorios(
        self, client: TestClient, headers_validos: dict
    ):
        """Resposta deve conter todos os campos do schema OptimizationResponse. Cobre: AC-2."""
        resp = client.post("/otimizar", json=PAYLOAD_VALIDO, headers=headers_validos)
        data = resp.json()

        assert "status_solver" in data
        assert "tempo_execucao_segundos" in data
        assert "barras_utilizadas" in data
        assert "desperdicio_total_mm" in data
        assert "plano_corte" in data
        assert isinstance(data["plano_corte"], list)

    def test_status_solver_e_valido(
        self, client: TestClient, headers_validos: dict
    ):
        """status_solver deve ser OPTIMAL, FEASIBLE ou INFEASIBLE."""
        resp = client.post("/otimizar", json=PAYLOAD_VALIDO, headers=headers_validos)
        data = resp.json()
        assert data["status_solver"] in ("OPTIMAL", "FEASIBLE", "INFEASIBLE")

    def test_invariante_comprimento_utilizado_mais_sobra(
        self, client: TestClient, headers_validos: dict
    ):
        """Para cada barra: comprimento_utilizado + sobra == comprimento_padrao."""
        resp = client.post("/otimizar", json=PAYLOAD_VALIDO, headers=headers_validos)
        data = resp.json()

        for barra in data["plano_corte"]:
            assert (
                barra["comprimento_utilizado"] + barra["sobra"]
                == PAYLOAD_VALIDO["comprimento_padrao"]
            ), (
                f"Invariante violada na barra {barra['barra_id']}: "
                f"{barra['comprimento_utilizado']} + {barra['sobra']} != {PAYLOAD_VALIDO['comprimento_padrao']}"
            )

    def test_time_limit_customizado_aceito(
        self, client: TestClient, headers_validos: dict
    ):
        """time_limit=30 deve ser aceito e retornar resultado. Cobre: AC-9."""
        payload = {**PAYLOAD_VALIDO, "time_limit": 30}
        resp = client.post("/otimizar", json=payload, headers=headers_validos)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status_solver"] in ("OPTIMAL", "FEASIBLE", "INFEASIBLE")

    def test_instancia_trivial_uma_barra(
        self, client: TestClient, headers_validos: dict
    ):
        """Instância trivial: 1 item que cabe exatamente em 1 barra → 1 barra usada."""
        payload = {
            "comprimento_padrao": 1000,
            "itens": [{"id": "A", "comprimento": 1000, "quantidade": 1}],
        }
        resp = client.post("/otimizar", json=payload, headers=headers_validos)
        assert resp.status_code == 200
        data = resp.json()
        assert data["barras_utilizadas"] == 1
        assert data["desperdicio_total_mm"] == 0

    def test_desperdicio_total_e_soma_das_sobras(
        self, client: TestClient, headers_validos: dict
    ):
        """desperdicio_total_mm deve ser a soma de todas as sobras do plano."""
        resp = client.post("/otimizar", json=PAYLOAD_VALIDO, headers=headers_validos)
        data = resp.json()
        soma_sobras = sum(b["sobra"] for b in data["plano_corte"])
        assert data["desperdicio_total_mm"] == soma_sobras
