---
name: tasks
description: Decomposição e gates da API de Otimização. Puxe ao implementar.
alwaysApply: false
---

# Tasks — API de Otimização para o Corte Unidimensional

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e tem um gate executável.

## Plano

| #  | Task                                                            | Cobre AC                    | Depende de | Gate (comando)                                        | Status |
|----|-----------------------------------------------------------------|-----------------------------|------------|-------------------------------------------------------|--------|
| 1  | Setup: venv, requirements.txt, estrutura de pastas             | —                           | —          | `python -m pytest --collect-only`                     | done   |
| 2  | `src/config.py` — variáveis de ambiente (.env)                  | AC-6, AC-7                  | 1          | `python -c "from src.config import settings"`         | done   |
| 3  | `src/schemas.py` — modelos Pydantic de entrada e saída          | AC-3, AC-4, AC-5, AC-10     | 1          | `pytest tests/test_solver.py::test_schemas -v`        | done   |
| 4  | `src/solver.py` — modelagem OR-Tools (Kantorovich) `[P]`        | AC-2, AC-8, AC-9            | 1          | `pytest tests/test_solver.py -v`                      | done   |
| 5  | `src/auth.py` — API Key dependency `[P]`                        | AC-6, AC-7                  | 2          | `pytest tests/test_api.py::test_auth -v`              | done   |
| 6  | `src/api.py` — FastAPI: /health, /otimizar, exception handler   | AC-1, AC-2, AC-11, AC-12   | 3, 4, 5    | `pytest tests/test_api.py -v`                         | done   |
| 7  | `tests/test_solver.py` — ≥ 6 testes unitários do solver         | AC-2, AC-3, AC-4, AC-5     | 4          | `pytest tests/test_solver.py -v --tb=short`           | done   |
| 8  | `tests/test_api.py` — ≥ 6 testes de integração da API           | AC-1..AC-12                 | 6          | `pytest tests/test_api.py -v --tb=short`              | done   |
| 9  | `.env.example`, `.gitignore`, `api_requests.http`               | AC-12 (segredos fora do git)| —          | `git status` (verificar que .env não aparece)         | done   |
| 10 | `render.yaml` e ajustes para deploy                             | AC-11 (URL pública)         | 6          | Deploy manual no Render                               | done   |
| 11 | README.md — URL pública, formulação, instalação                 | Rubrica 1.0                 | 10         | Revisão manual                                        | done   |

## Plano de teste

- **Unitário (test_solver.py):**
  - Instância trivial: 1 item, 1 barra exata (sem sobra)
  - Instância do projeto_final (3 itens, resultado conhecido)
  - Validação de demanda negativa (schema)
  - Validação de item maior que a barra (schema)
  - Validação de time_limit > 120 (schema)
  - Solver com time_limit pequeno retorna FEASIBLE ou OPTIMAL

- **Integração (test_api.py):**
  - GET /health retorna 200 {"status":"ok"}
  - POST /otimizar sem API Key → 403
  - POST /otimizar com API Key errada → 403
  - POST /otimizar com payload inválido → 422
  - POST /otimizar payload válido → 200 + estrutura correta
  - POST /otimizar com time_limit=200 → 422
  - Invariante: comprimento_utilizado + sobra == comprimento_padrao em todas as barras
  - Invariante: demanda suprida (soma dos itens cortados >= quantidade pedida)

## Divergências (SPEC_DEVIATION)

> Nenhuma até o momento.

## Checklist de Definition of Done

- [x] Todos os AC verdes pelo gate executável (`pytest tests/ -v`)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] ADRs registrados: 0002, 0003, 0004
- [x] Glossário atualizado em `docs/glossary.md`
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado
