---
name: STATE
description: Memória de trabalho volátil — onde paramos, próximo passo, bloqueios.
alwaysApply: true
---

# STATE — Memória viva do projeto

> Memória de trabalho **entre sessões**. **Volátil**: atualizada constantemente.
> Diferente do **ADR** (decisão durável e imutável). Atualize ao pausar/encerrar; leia ao retomar.

**Última atualização:** 2026-07-06 por Antigravity (agente de IA)

## Status geral

**Feature ativa:** `specs/0001-api-otimizacao/` — **TODA A DOCUMENTAÇÃO SDD CONCLUÍDA** ✅

**Resultado dos testes:** 34 passed · 97% coverage (linha de base da Onda 1)

## Próximo passo imediato

**Fazer o deploy no Render:**

1. Inicializar Git e fazer push:
   ```bash
   git init
   git add .
   git commit -m "feat: Onda 1 MVP — API de Otimização de Corte Unidimensional"
   git remote add origin https://github.com/<seu-usuario>/OptimizationAAService.git
   git push -u origin main
   ```
2. Acessar [render.com](https://render.com) → New → Web Service → conectar o repositório
3. Configurar `API_KEY` no painel de Environment Variables
4. Aguardar o deploy (o `render.yaml` define tudo automaticamente)
5. Após o deploy: atualizar a URL no topo do `README.md`

## O que foi concluído — Onda 1 MVP

### Código
- [x] `src/config.py` — pydantic-settings
- [x] `src/schemas.py` — Pydantic v2 com validação rigorosa
- [x] `src/auth.py` — API Key via `X-API-Key`
- [x] `src/solver.py` — OR-Tools CP-SAT + Kantorovich
- [x] `src/api.py` — FastAPI: `/health`, `/otimizar`, handler de erros

### Testes
- [x] `tests/test_solver.py` — 16 testes unitários (schemas + solver)
- [x] `tests/test_api.py` — 18 testes de integração (endpoints HTTP)
- [x] Cobertura: **97%** (meta: ≥ 80%)

### Infraestrutura
- [x] `requirements.txt` — dependências pinadas
- [x] `.env.example` — template de variáveis de ambiente
- [x] `.gitignore` — .env bloqueado
- [x] `render.yaml` — deploy declarativo no Render
- [x] `pytest.ini` — configuração do pytest
- [x] `api_requests.http` — exemplos de requisições

### Documentação SDD (completa)
- [x] `specs/0001-api-otimizacao/spec.md` — 12 critérios de aceite
- [x] `specs/0001-api-otimizacao/design.md` — Technical Design Doc (5 eixos)
- [x] `specs/0001-api-otimizacao/product.md` — contexto de produto
- [x] `specs/0001-api-otimizacao/domain.md` — modelo de domínio
- [x] `specs/0001-api-otimizacao/tasks.md` — 11 tasks com gates executáveis
- [x] `docs/architecture/adr/0001-record-architecture-decisions.md`
- [x] `docs/architecture/adr/0002-api-key-auth.md`
- [x] `docs/architecture/adr/0003-ortools-kantorovich.md`
- [x] `docs/architecture/adr/0004-render-deploy.md`
- [x] `docs/glossary.md` — linguagem ubíqua completa (23 termos)
- [x] `docs/architecture/context-map.md` — 3 bounded contexts + relações
- [x] `docs/architecture/overview.md` — 5 eixos + segurança + operacional
- [x] `docs/architecture/diagrams.md` — C4 L1, C4 L2, context map, sequence, file tree
- [x] `docs/engineering/TESTING.md` — comandos reais + mapa AC→Teste
- [x] `docs/engineering/metrics.md` — baseline Onda 1 (97% cobertura)
- [x] `docs/product/vision.md` — declaração working-backwards + personas
- [x] `docs/product/roadmap.md` — Ondas 1, 2, 3
- [x] `src/README.md` — mapeamento DDD dos módulos
- [x] `README.md` — manual completo com formulação matemática + endpoints

## Bloqueios

- [ ] Deploy no Render — requer ação manual (push para GitHub + conectar no Render)
- [ ] URL pública não gerada — depende do deploy
- [ ] `<seu-usuario>` no README.md — substituir pelo usuário real do GitHub

## Decisões duráveis (ADRs)

| ADR  | Decisão                                | Status   |
|------|----------------------------------------|----------|
| 0001 | Registrar decisões como ADRs           | aceito   |
| 0002 | API Key para autenticação              | aceito   |
| 0003 | OR-Tools CP-SAT + Kantorovich          | aceito   |
| 0004 | Render como plataforma de deploy       | aceito   |

## Ideias adiadas / backlog (Onda 2+)

- CI com GitHub Actions (lint + testes)
- Logs estruturados (JSON) com request_id
- Rate limiting por API Key
- Corte bidimensional (2D-CSP)
- Persistência de histórico de requisições
