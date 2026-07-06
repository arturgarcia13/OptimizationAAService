---
name: roadmap
description: Roadmap incremental do produto. Consulte ao priorizar e sequenciar próximas features.
alwaysApply: false
---

# Roadmap — Optimization-as-a-Service

> Roadmap incremental baseado em valor × esforço. Cada onda entrega algo funcional.
> A Onda 1 é o MVP da disciplina. As ondas seguintes são backlog pós-entrega.

## Onda 1 — MVP (2026.1 — entregue ✅)

**Meta:** API REST pública, documentada, segura e testada para o Projeto Final da disciplina.

| # | Feature                                | AC relacionados      | Status |
|---|----------------------------------------|----------------------|--------|
| 1 | `GET /health` — liveness probe         | AC-1                 | ✅     |
| 2 | `POST /otimizar` — solver OR-Tools     | AC-2, AC-8, AC-9    | ✅     |
| 3 | Autenticação API Key (`X-API-Key`)     | AC-6, AC-7           | ✅     |
| 4 | Validação Pydantic v2 (422)            | AC-3, AC-4, AC-5, AC-10 | ✅  |
| 5 | Swagger rico (`/docs`)                 | AC-11                | ✅     |
| 6 | Proteção de tracebacks em produção     | AC-12                | ✅     |
| 7 | Suíte ≥ 10 testes + cobertura ≥ 80%   | todos ACs            | ✅     |
| 8 | Deploy online Render + URL no README   | —                    | ⏳     |

**Gate de conclusão:** `python -m pytest tests/ -v` — 34 passed · 97% coverage

---

## Onda 2 — Estabilização (pós-entrega)

**Meta:** melhorar a robustez e observabilidade da API em produção.

| # | Feature                              | Motivação                                         | Esforço |
|---|--------------------------------------|---------------------------------------------------|---------|
| 1 | GitHub Actions CI (lint + testes)    | Automatizar gate em cada PR                      | Pequeno |
| 2 | Logs estruturados (JSON) com request_id | Facilitar debugging em produção              | Pequeno |
| 3 | Endpoint `GET /metrics` (básico)     | Expor tempo médio e contagem de requests         | Médio   |
| 4 | Rate limiting por API Key            | Prevenir abuso de recursos no free tier          | Médio   |

---

## Onda 3 — Evolução do solver (futuro)

**Meta:** ampliar as capacidades de otimização.

| # | Feature                                     | Motivação                                           | Esforço      |
|---|---------------------------------------------|-----------------------------------------------------|--------------|
| 1 | Suporte a múltiplos tipos de barra padrão   | Cenários com estoque misto                         | Arquitetural |
| 2 | Corte bidimensional (2D-CSP)                | Indústria de chapas (vidro, MDF)                   | Arquitetural |
| 3 | Persistência de histórico de requisições   | Auditoria e replay de cenários                     | Arquitetural |
| 4 | Comparação de heurísticas vs ótimo         | Ferramenta de pesquisa acadêmica                   | Médio        |

---

## Princípios de priorização

1. **Valor para o usuário primeiro** — cada onda entrega algo usável
2. **Decisões difíceis de reverter → ADR antes de implementar**
3. **Tier arquitetural (Onda 3) requer `design.md` aprovado antes de codificar**
4. **Onda 2+ só começa após a URL pública da Onda 1 estar estável**
