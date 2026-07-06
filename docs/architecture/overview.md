---
name: architecture-overview
description: Arquitetura do sistema nos 5 eixos + segurança e operacional. Puxe ao trabalhar em arquitetura, infra, qualidade, observabilidade ou segurança.
alwaysApply: false
---

# Arquitetura do sistema — Optimization-as-a-Service

> Visão **consolidada** do sistema pelos 5 eixos (+ segurança e operacional).
> Cada seção é um resumo curto + link para o detalhe (ADRs, context-map, diagrams, TESTING).
> **Mantenha enxuto** — o detalhe vive nos docs linkados, aqui é o mapa.

## 1. Tech stack

| Componente       | Tecnologia        | Versão  |
|------------------|-------------------|---------|
| Linguagem        | Python            | 3.12    |
| Framework web    | FastAPI           | 0.115.x |
| Validação        | Pydantic v2       | 2.10.x  |
| Solver           | OR-Tools (CP-SAT) | 9.15.x  |
| Config           | pydantic-settings | 2.6.x   |
| Servidor ASGI    | uvicorn           | 0.32.x  |
| Testes           | pytest + cov      | 8.3.x   |

- Decisão solver: [ADR-0003](adr/0003-ortools-kantorovich.md)
- Stack definido em: [design.md](../../specs/0001-api-otimizacao/design.md#1-tech-stack)

## 2. Arquitetura base

**Estilo:** Monolito modular (single service), arquitetura em camadas:

```
interfaces (api.py) → application (solver.py) → domain (schemas.py) ← infrastructure (config.py)
```

- **Bounded context único:** `Otimização de Corte` (com módulos de Autenticação e Configuração como supporting)
- Mapa de contextos: [context-map.md](context-map.md)
- Diagramas: [diagrams.md](diagrams.md)
- Design detalhado: [specs/0001-api-otimizacao/design.md](../../specs/0001-api-otimizacao/design.md)

## 3. Infra

| Aspecto     | Decisão                                                  |
|-------------|----------------------------------------------------------|
| Provedor    | Render (free tier)                                       |
| Deploy      | Push to main → auto-deploy via `render.yaml`            |
| IaC         | `render.yaml` declarativo versionado no repo            |
| Ambientes   | local (`.env`) + produção (Render env vars)             |
| Custo       | $0 (free tier)                                          |

- Decisão: [ADR-0004](adr/0004-render-deploy.md)
- Operacional: ver seção 7.

## 4. Qualidade

| Nível     | Comando                                                         | Meta    |
|-----------|-----------------------------------------------------------------|---------|
| Unitário  | `pytest tests/test_solver.py -v`                                | 100%    |
| Integração| `pytest tests/test_api.py -v`                                   | 100%    |
| Cobertura | `pytest --cov=src --cov-report=term-missing`                    | ≥ 80%   |

**Resultado atual:** 34 testes · **97% de cobertura** (acima da meta)

- Comandos e gates completos: [TESTING.md](../engineering/TESTING.md)

## 5. Observabilidade

| Aspecto    | Implementação                                              |
|------------|------------------------------------------------------------|
| Logs       | `logging.INFO` em cada request e resultado do solver      |
| Métricas   | `tempo_execucao_segundos` em toda resposta de otimização  |
| Alertas    | Render UI notifica falha no health check (`/health`)      |
| Erros      | Handler global — loga stack trace; cliente vê msg genérica|

- Tracing distribuído: fora do escopo MVP

## 6. Segurança

| Controle                | Implementação                                                |
|-------------------------|--------------------------------------------------------------|
| Autenticação            | API Key via `X-API-Key` (comparação constante contra `API_KEY` do env) |
| Autorização             | Binária: chave válida → acesso total; inválida → 403        |
| Proteção de segredos    | `.env` bloqueado no `.gitignore`; produção via Render env vars |
| Ocultação de tracebacks | `exception_handler` global retorna msg genérica em produção |
| Validação de entrada    | Pydantic v2 rejeita malformados com 422 antes de processar  |
| Proteção de recursos    | `time_limit` (máx. 120s) previne abuso de CPU              |

- Decisão autenticação: [ADR-0002](adr/0002-api-key-auth.md)

## 7. Operacional

| Aspecto      | Procedimento                                                      |
|--------------|-------------------------------------------------------------------|
| Deploy       | `git push origin main` → Render faz build + deploy automático   |
| Rollback     | `git revert HEAD && git push` → Render redeploy na versão anterior|
| Monitoramento| Render dashboard + logs do serviço                               |
| Rotação de chave | Atualizar `API_KEY` no painel Render + redeploy             |
| Health check | Render monitora `GET /health` e reinicia se falhar               |
