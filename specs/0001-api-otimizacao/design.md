---
name: design
description: Technical Design Doc da API de Otimização. Puxe ao trabalhar em arquitetura ou tomar decisões estruturais.
alwaysApply: false
---

# Technical Design Doc — API de Otimização para o Corte Unidimensional

> **Tier:** arquitetural · **Status:** aprovado
> **Autor:** Equipe UFC 2026.1 · **Data:** 2026-07-06
> Responde: **como** no nível de sistema. Obrigatório no tier arquitetural.

## Links e artefatos

| Artefato                 | Onde                       | Link                                            |
|--------------------------|----------------------------|-------------------------------------------------|
| Spec · Product · Domínio | repositório                | `./spec.md` · `./product.md` · `./domain.md`  |
| ADR Autenticação         | repositório                | [ADR-0002](../../docs/architecture/adr/0002-api-key-auth.md) |
| ADR Solver               | repositório                | [ADR-0003](../../docs/architecture/adr/0003-ortools-kantorovich.md) |
| ADR Deploy               | repositório                | [ADR-0004](../../docs/architecture/adr/0004-render-deploy.md) |

## Contexto da funcionalidade

A disciplina "Laboratório de Otimização" da UFC (2026.1) exige o desenvolvimento de um serviço
REST completo que resolve o **Problema de Corte Unidimensional** (1D Cutting Stock Problem) via
**Google OR-Tools**, com autenticação, validação rigorosa, limite de tempo configurável e
publicação online. O projeto parte do zero (greenfield) num repositório já com a estrutura
SDD boilerplate.

**Problema:** não existe hoje nenhum serviço público gratuito que disponibilize o solver de
Kantorovich para o corte unidimensional via API REST — o projeto preenche essa lacuna enquanto
atende os critérios da rubrica (10 pontos).

## Goals / Non-goals

**Goals**
- Expor o solver OR-Tools como serviço REST (`POST /otimizar`) com retorno estruturado
- Autenticar requisições via API Key (simples, segura, sem estado)
- Validar entradas com Pydantic v2 (rejeitar malformadas com 422)
- Limitar o tempo do solver (1–120s) para confiabilidade e proteção de recursos
- Documentar automaticamente via Swagger/OpenAPI (`GET /docs`)
- Publicar online no Render com CI implícita (push → deploy)
- Atingir ≥ 80% de cobertura de testes (mínimo da disciplina)

**Non-goals**
- Corte bidimensional ou tridimensional
- Frontend/interface gráfica de visualização
- Persistência de histórico de requisições
- Rate limiting por cliente
- Múltiplos comprimentos padrão de barra por requisição
- JWT / OAuth2 (descartado — ver ADR-0002)

## Glossário (da funcionalidade)

| Termo                    | Descrição                                                       |
|--------------------------|-----------------------------------------------------------------|
| Corte Unidimensional     | Problema de otimizar o corte de barras lineares para minimizar desperdício |
| Formulação de Kantorovich | Modelo MIP com variáveis yⱼ (barra usada) e xᵢⱼ (qtd item i na barra j) |
| CP-SAT                   | Constraint Programming + SAT: solver do OR-Tools usado neste projeto |
| API Key                  | Token estático compartilhado que autentica cada requisição HTTP |
| time_limit               | Limite de tempo (s) que o solver pode usar antes de retornar o melhor resultado |

> Todos os termos de domínio estão em `docs/glossary.md`.

## Design proposto

### Visão geral — arquitetura em camadas

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENTE (curl/app)                       │
│  POST /otimizar + X-API-Key                                  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
┌───────────────────────────▼─────────────────────────────────┐
│              INTERFACES — src/api.py (FastAPI)               │
│  GET /health · POST /otimizar · exception_handler (AC-12)    │
└───────┬──────────────────┬──────────────────┬───────────────┘
        │ Depends          │ Input            │ Output
┌───────▼──────┐  ┌────────▼───────┐  ┌──────▼──────────────┐
│ src/auth.py  │  │ src/schemas.py │  │ src/schemas.py       │
│ API Key dep  │  │ Pydantic v2    │  │ OptimizationResponse │
│ (AC-6, AC-7) │  │ (AC-3..AC-5)  │  │                      │
└──────────────┘  └────────┬───────┘  └──────────────────────┘
                           │ OptimizationRequest validated
┌──────────────────────────▼──────────────────────────────────┐
│              APPLICATION — src/solver.py                     │
│  resolver_corte(comprimento, itens, time_limit)              │
│  Formulação de Kantorovich com CP-SAT (OR-Tools)             │
│  Upper bound N = Σdᵢ  · simetria · quebra de simetria       │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              INFRA — src/config.py                           │
│  pydantic-settings → lê .env / variáveis de ambiente        │
│  API_KEY · time limits · debug mode                         │
└──────────────────────────────────────────────────────────────┘
```

### Fluxo de uma requisição de otimização

```
Cliente ──POST /otimizar──► FastAPI
                               │
                         verify_api_key (auth.py)
                               │ 403 se ausente/incorreta
                               ▼
                         OptimizationRequest (schemas.py)
                               │ 422 se inválida
                               ▼
                         resolver_corte (solver.py)
                               │
                         CpModel (OR-Tools CP-SAT)
                               │  variáveis y[j], x[i][j]
                               │  restrições demanda + capacidade
                               │  objetivo: minimizar Σy[j]
                               │  time_limit configurado
                               ▼
                         OptimizationResponse (schemas.py)
                               │
                         200 OK ◄────── Cliente
```

### Estrutura de arquivos

```
src/
├── api.py       # interfaces — endpoints FastAPI + exception handler
├── auth.py      # dependency de autenticação (API Key)
├── schemas.py   # contratos Pydantic (entrada e saída)
├── solver.py    # lógica de otimização (OR-Tools CP-SAT)
└── config.py    # configurações via pydantic-settings

tests/
├── test_solver.py  # testes unitários (schemas + solver)
└── test_api.py     # testes de integração (endpoints completos)
```

## Cobertura dos 5 eixos

### 1. Tech stack

| Componente       | Tecnologia           | Versão    | Motivo                                           |
|------------------|----------------------|-----------|--------------------------------------------------|
| Framework web    | FastAPI              | 0.115.x   | Async, OpenAPI nativo, DI elegante               |
| Validação        | Pydantic v2          | 2.10.x    | Rápido, type-safe, mensagens de erro ricas       |
| Solver           | OR-Tools (CP-SAT)    | 9.15.x    | Gratuito, Python-nativo, ótimo para MIP small-medium |
| Config           | pydantic-settings    | 2.6.x     | Lê .env de forma tipada                          |
| Servidor         | uvicorn              | 0.32.x    | ASGI production-ready                            |
| Testes           | pytest + pytest-cov  | 8.3.x     | Padrão Python, fixture-based                     |
| HTTP client test | httpx                | 0.28.x    | Necessário para TestClient do FastAPI            |

**Divergência do stack padrão:** nenhuma — o stack é definido aqui como o padrão deste projeto.

### 2. Arquitetura base

O projeto segue uma **arquitetura em camadas simplificada** (adequada ao escopo de um único serviço):

- **interfaces** (`api.py`): recebe HTTP, delega, serializa resposta
- **application** (`solver.py`): orquestra o caso de uso
- **domain** (`schemas.py`): modelos e invariantes de negócio
- **infrastructure** (`config.py`): lê ambiente externo

Não há banco de dados, filas ou sistemas externos além do OR-Tools (biblioteca local).
**Bounded context único:** `Otimização de Corte` — não há integração com outros contextos.

### 3. Infra

| Aspecto        | Decisão                                                           |
|----------------|-------------------------------------------------------------------|
| Provedor       | Render (free tier) — ver ADR-0004                                |
| Ambientes      | local (`.env`) + produção (Render env vars)                      |
| Deploy         | Push to main → Render auto-deploy via `render.yaml`              |
| IaC            | `render.yaml` declarativo versionado no repo                     |
| Custo          | $0 (free tier — aceita cold start de ~30s após inatividade)      |
| Reversão       | Git revert + novo push → Render faz redeploy automático          |

**Riscos de infra:**
- Cold start no free tier → documentado no README para o avaliador
- Sem persistent disk → sem estado entre requests (comportamento desejado)

### 4. Qualidade

| Nível        | Framework    | Gate (comando)                                                  | Meta      |
|--------------|--------------|------------------------------------------------------------------|-----------|
| Unitário     | pytest       | `pytest tests/test_solver.py -v`                                | 100% pass |
| Integração   | pytest+httpx | `pytest tests/test_api.py -v`                                   | 100% pass |
| Cobertura    | pytest-cov   | `pytest --cov=src --cov-report=term-missing`                    | ≥ 80%     |
| Type check   | mypy (opt.)  | `mypy src/ --ignore-missing-imports`                            | sem erros |
| Lint         | ruff (opt.)  | `ruff check src/ tests/`                                        | sem erros |

**Resultado atual:** 34 testes passando · **97% de cobertura** (acima da meta de 80%).

### 5. Observabilidade

| Aspecto       | Implementação                                                |
|---------------|--------------------------------------------------------------|
| Logs          | `logging.basicConfig(level=INFO)` — cada request logado     |
| Métricas      | `tempo_execucao_segundos` retornado em toda resposta        |
| Tracing       | Sem distributed tracing (escopo MVP — ver Non-goals)         |
| Alertas       | Render UI notifica falha no health check                    |
| Erros         | Handler global captura e loga stack trace; cliente recebe msg genérica |

## Mapa de dependências

| Dependência      | Tipo        | Descrição                            | Principais interfaces                              |
|------------------|-------------|--------------------------------------|----------------------------------------------------|
| OR-Tools CP-SAT  | biblioteca  | Solver de otimização combinatória    | `cp_model.CpModel`, `CpSolver.solve()`            |
| FastAPI          | framework   | Web framework ASGI                   | `@app.get`, `@app.post`, `Depends`                |
| Pydantic v2      | biblioteca  | Validação e serialização de dados    | `BaseModel`, `Field`, `model_validator`            |
| pydantic-settings| biblioteca  | Leitura de variáveis de ambiente     | `BaseSettings`, `SettingsConfigDict`               |
| uvicorn          | servidor    | ASGI server para produção e dev      | `uvicorn.run()` / CLI                             |
| httpx            | teste       | HTTP client para TestClient FastAPI  | `TestClient`                                      |
| Render           | plataforma  | Hospedagem do serviço                | `render.yaml`, painel de Environment Variables    |

## Alternativas consideradas

| Alternativa              | Prós                                    | Contras                                             | Decisão              |
|--------------------------|-----------------------------------------|-----------------------------------------------------|----------------------|
| **OR-Tools CP-SAT** ✅  | Gratuito, Python-nativo, ótimo p/ MIP   | Pode ser lento em N muito grande                   | Escolhido (ADR-0003) |
| Heurística FFD           | Muito rápido, fácil de implementar      | Não garante ótimo — inaceitável para a disciplina  | Descartado           |
| Column Generation        | Melhor escala para instâncias grandes   | Muito complexo para o escopo do projeto            | Descartado           |
| **API Key** ✅           | Simples, sem estado, testável           | Sem expiração automática                           | Escolhido (ADR-0002) |
| JWT                      | Expiração nativa, revogação granular    | Overhead (endpoint login, gestão de tokens)        | Descartado (ADR-0002)|
| **Render** ✅            | Free tier, deploy declarativo, simples  | Cold start após inatividade                        | Escolhido (ADR-0004) |
| Railway                  | Interface moderna                       | Free tier mais restrito em 2026                    | Descartado           |
| Hugging Face Spaces      | Ótimo para demos ML                     | Requer Dockerfile, menos padrão para APIs REST     | Descartado           |

## Trade-offs e consequências

**O que ganhamos:**
- Solução ótima garantida (OPTIMAL) para instâncias típicas da disciplina (< 50 itens)
- Implementação simples e limpa (< 300 linhas de código produtivo)
- Documentação Swagger rica sem configuração extra (FastAPI nativo)
- 97% de cobertura de testes com 34 testes distintos

**O que aceitamos:**
- Cold start de ~30s no Render free tier após inatividade (documentado no README)
- API Key sem expiração automática (troca requer redeploy)
- Sem persistência de histórico (stateless por design)
- Para instâncias com N > 500, o solver pode não encontrar OPTIMAL dentro de 120s (retorna FEASIBLE)

## Riscos

| Risco                         | Descrição                                              | Prob × Impacto | Mitigação                                              |
|-------------------------------|--------------------------------------------------------|----------------|--------------------------------------------------------|
| Timeout do solver em N grande | Instâncias com muitos itens podem ultrapassar 120s    | Baixa × Média  | time_limit garante retorno de FEASIBLE; documentado    |
| Vazamento de API Key          | Key comprometida permite uso não autorizado            | Baixa × Alta   | Rotacionar via redeploy no Render; .gitignore bloqueia |
| Cold start Render             | Avaliador pode confundir com lentidão do solver       | Média × Baixa  | README documenta o comportamento; health check rápido  |
| Compatibilidade OR-Tools      | Versão nova pode quebrar a API do CP-SAT              | Baixa × Média  | Versão pinada no requirements.txt; testes como gate   |

## Roadmap da feature

| Fase / onda | Entrega                                              | Quando   | Depende de |
|-------------|------------------------------------------------------|----------|------------|
| 1 (MVP) ✅  | API completa: /health, /otimizar, auth, validação    | 2026-07  | —          |
| 1 (MVP) ✅  | Suíte de 34 testes com 97% de cobertura              | 2026-07  | —          |
| 2 ⏳         | Deploy online no Render com URL pública              | 2026-07  | Fase 1     |
| 3 (futuro)  | Rate limiting por cliente                            | pós-MVP  | Fase 2     |
| 3 (futuro)  | Persistência de histórico de requisições             | pós-MVP  | Fase 2     |

## Questões em aberto

- [x] Método de autenticação → API Key (ADR-0002)
- [x] Solver e formulação → OR-Tools CP-SAT + Kantorovich (ADR-0003)
- [x] Plataforma de deploy → Render (ADR-0004)
- [ ] URL pública final → pendente de deploy no Render (próximo passo)
