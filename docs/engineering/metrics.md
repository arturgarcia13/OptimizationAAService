---
name: metrics
description: Métricas de entrega — Lead Time, Throughput, qualidade de código (cobertura). Puxe ao revisar o fluxo ou planejar.
alwaysApply: false
---

# Métricas de entrega — Optimization-as-a-Service

> Saúde do fluxo: **Lead Time**, **Throughput** e qualidade de código.
> Use para **achar gargalo**, não para ranquear pessoas.

**Período:** 2026-07-01 a 2026-07-06 (Onda 1 — MVP)
**Atualizado em:** 2026-07-06

## Lead Time — tempo até produção

> Do início (spec / issue / 1º commit) ao deploy em prod. Reporte **mediana** e **p85**.

| Item                              | Início       | Em prod  | Lead time |
|-----------------------------------|--------------|----------|-----------|
| spec + design + ADRs              | 2026-07-06   | —        | 1 sessão  |
| src/config.py, schemas.py, auth.py| 2026-07-06   | —        | 1 sessão  |
| src/solver.py (Kantorovich)       | 2026-07-06   | —        | 1 sessão  |
| src/api.py (FastAPI)              | 2026-07-06   | —        | 1 sessão  |
| tests/ (34 testes)                | 2026-07-06   | —        | 1 sessão  |
| Infraestrutura (render.yaml, .env)| 2026-07-06   | —        | 1 sessão  |
| Docs SDD (glossary, diagrams, …)  | 2026-07-06   | —        | 1 sessão  |

- **Mediana:** < 1 dia · **p85:** < 1 dia · **Tendência:** ↑ (projeto novo)
- **Nota:** desenvolvido em sessão única com assistência agêntica (Antigravity)

## Throughput — itens concluídos na Onda 1

| Tipo                          | Concluídos |
|-------------------------------|------------|
| Features (endpoints)          | 2          |
| Tasks da spec                 | 11         |
| Testes automatizados          | 34         |
| ADRs registrados              | 4          |
| Docs SDD criados/atualizados  | 15         |
| **Total de artefatos**        | **66**     |

- **Tendência vs ciclo anterior:** N/A (primeiro ciclo)

## Continuous Delivery / Deployment

| Prática                                    | Estado atual       | Gap para avançar               |
|--------------------------------------------|--------------------|--------------------------------|
| Continuous Delivery (deployável sempre)    | parcial            | Deploy no Render pendente      |
| Continuous Deployment (deploy automático)  | sim (via Render)   | Após conectar o repositório    |

- **Deployment Frequency:** 0 deploys (URL pública ainda não configurada)
- Próximo passo: conectar repo no Render → push to main → deploy automático

## Qualidade de código

> Evidência rastreável: cobertura medida com `pytest-cov` em 2026-07-06.

### Cobertura (resultado atual — baseline da Onda 1)

| Módulo            | Atual  | Mínimo | Tendência |
|-------------------|--------|--------|-----------|
| `src/__init__.py` | 100%   | ≥ 80%  | →         |
| `src/api.py`      | 87%    | ≥ 80%  | →         |
| `src/auth.py`     | 100%   | ≥ 80%  | →         |
| `src/config.py`   | 100%   | ≥ 80%  | →         |
| `src/schemas.py`  | 100%   | ≥ 80%  | →         |
| `src/solver.py`   | 98%    | ≥ 80%  | →         |
| **Global**        | **97%**| ≥ 80%  | →         |

### Análise estática

| Categoria             | Findings | Bloqueantes | Tendência |
|-----------------------|----------|-------------|-----------|
| Type-check (mypy)     | —        | —           | (não medido ainda) |
| Complexidade / smells | baixa    | 0           | →         |
| Segurança (SAST)      | —        | —           | (não medido ainda) |
| Duplicação            | mínima   | —           | →         |

> **Nota:** type-check e SAST são opcionais neste ciclo (ver TESTING.md). Recomendados na Onda 2.
