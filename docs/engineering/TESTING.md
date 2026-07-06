---
name: TESTING
description: Comandos de gate e convenções de teste. Puxe ao codar, validar ou montar CI.
alwaysApply: false
---

# TESTING — Como verificar o projeto

> **Fonte única dos comandos de gate** e das convenções de teste. É o que o **DoD**, a **CI** e os
> **subagentes** consomem para provar que uma task/feature está pronta — sem inspeção visual.

## Pré-requisito: ativar o ambiente virtual

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

Se o venv não existir ainda:
```bash
python -m venv .venv
pip install -r requirements.txt
cp .env.example .env   # edite API_KEY
```

## Como rodar

| Nível             | Comando                                                              | Quando               |
|-------------------|----------------------------------------------------------------------|----------------------|
| **Todos**         | `python -m pytest tests/ -v`                                         | sempre               |
| Unitário          | `python -m pytest tests/test_solver.py -v`                           | rápido, isolado      |
| Integração        | `python -m pytest tests/test_api.py -v`                              | endpoints completos  |
| Cobertura         | `python -m pytest --cov=src --cov-report=term-missing`               | CI / pré-PR         |
| Cobertura HTML    | `python -m pytest --cov=src --cov-report=html`                       | análise visual       |
| Lint (opcional)   | `ruff check src/ tests/` (instalar: `pip install ruff`)              | pré-commit / CI     |
| Type-check (opt.) | `mypy src/ --ignore-missing-imports` (instalar: `pip install mypy`)  | CI                   |

> **Windows:** use `python -m pytest` em vez de `pytest` diretamente para garantir que o venv
> correto seja usado. Alternativamente: `.venv\Scripts\pytest`.

## Resultado esperado (linha de base atual)

```
34 passed in ~12s
Coverage: 97% (acima do mínimo de 80% exigido)
```

## Convenções

- **Pirâmide:** 16 unitários (schemas + solver puro) + 18 de integração (endpoints FastAPI)
- **Rastreabilidade:** cada teste mapeia para um `AC-N` da `specs/0001-api-otimizacao/spec.md`
- **Nomenclatura:** `test_<ac_descricao>` ou classes `TestAC1_*` / `TestSolverOtimizacaoBasica`
- **Domínio isolado:** `test_solver.py` não usa HTTP — testa o modelo e os schemas diretamente
- **Integração:** `test_api.py` usa `TestClient(app)` do FastAPI + `httpx`

## Gates (Definition of Done executável)

Uma **task** do `tasks.md` só vira `done` quando o Gate (comando) dela passa.

Uma **feature** só está pronta quando:
- [ ] `python -m pytest tests/ -v` — todos passam
- [ ] `python -m pytest --cov=src --cov-report=term-missing` — cobertura ≥ 80%
- [ ] Nenhum `SPEC_DEVIATION` pendente em `tasks.md`
- [ ] Todos os `AC-N` da spec verificados pelo gate

## Mapa AC → Teste (rastreabilidade spec → teste)

| AC    | Critério de aceite                         | Arquivo            | Teste(s)                                              |
|-------|--------------------------------------------|--------------------|-------------------------------------------------------|
| AC-1  | GET /health retorna 200 {status: ok}       | test_api.py        | `TestHealthEndpoint::test_health_retorna_200/status_ok` |
| AC-2  | POST /otimizar → 200 + plano_corte         | test_api.py        | `TestOtimizacao::test_payload_valido_*`               |
| AC-3  | comprimento_padrao inválido → 422          | test_api.py, test_solver.py | `test_comprimento_padrao_zero_*`           |
| AC-4  | item maior que barra → 422                 | test_api.py, test_solver.py | `test_item_comprimento_maior_*`            |
| AC-5  | quantidade ≤ 0 → 422                       | test_api.py, test_solver.py | `test_quantidade_zero_*`                   |
| AC-6  | sem X-API-Key → 403                        | test_api.py        | `TestAutenticacao::test_sem_api_key_*`                |
| AC-7  | X-API-Key inválida → 403                   | test_api.py        | `TestAutenticacao::test_api_key_invalida_*`           |
| AC-8  | time_limit padrão = 60s                    | test_solver.py     | `test_solver_respeita_time_limit_pequeno`             |
| AC-9  | time_limit customizado aceito              | test_api.py        | `TestOtimizacao::test_time_limit_customizado_aceito`  |
| AC-10 | time_limit > 120 → 422                     | test_api.py, test_solver.py | `test_time_limit_acima_*`                  |
| AC-11 | GET /docs retorna 200 (Swagger)            | test_api.py        | `TestHealthEndpoint::test_swagger_docs_acessivel`     |
| AC-12 | sem traceback em erros                     | test_api.py        | `TestAutenticacao::test_403_sem_traceback_exposto`    |

## O que a CI deveria executar

```yaml
# Ordem sugerida para pipeline CI (ex: GitHub Actions)
jobs:
  test:
    steps:
      - name: Instalar dependências
        run: pip install -r requirements.txt
      - name: Unitários + integração
        run: python -m pytest tests/ -v --tb=short
      - name: Cobertura (gate ≥ 80%)
        run: python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80
      - name: Lint (opcional)
        run: ruff check src/ tests/ || true
```
