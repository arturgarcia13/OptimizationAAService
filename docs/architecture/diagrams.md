---
name: diagrams
description: Diagramas de arquitetura (Mermaid). Puxe ao desenhar ou rever a arquitetura.
alwaysApply: false
---

# Diagramas de arquitetura — Optimization-as-a-Service

> Alto nível (C4 L1–L2 + mapa de bounded contexts + fluxo de requisição).
> Renderiza no GitHub e no Antigravity/Claude. Rótulos na linguagem ubíqua do `glossary.md`.

## 1. Contexto do sistema (C4 L1)

```mermaid
flowchart LR
    DEV(["👤 Desenvolvedor\n(curl / app / Swagger UI)"])
    SYS["🔧 Optimization-as-a-Service\n(API REST Python/FastAPI)\nRender · Python 3.12"]
    ORT["📦 OR-Tools CP-SAT\n(biblioteca local)"]

    DEV -- "POST /otimizar\nX-API-Key + payload JSON\n(HTTPS)" --> SYS
    DEV -- "GET /health\nGET /docs" --> SYS
    SYS -- "resolve(model)\ntime_limit=60s" --> ORT
    ORT -- "status + solução ótima" --> SYS
    SYS -- "200 OK + plano_corte\nou 403/422/500" --> DEV
```

## 2. Containers (C4 L2)

```mermaid
flowchart TB
    subgraph Render["☁️ Render (free tier)"]
        API["🌐 FastAPI\nsrc/api.py\nuvicorn :$PORT"]
        AUTH["🔐 Auth Module\nsrc/auth.py\nverify_api_key()"]
        SCHEMA["📋 Schemas\nsrc/schemas.py\nPydantic v2"]
        SOLVER["⚙️ Solver\nsrc/solver.py\nOR-Tools CP-SAT"]
        CONFIG["⚙️ Config\nsrc/config.py\npydantic-settings"]
        ENV[("🔑 Env Vars\nAPI_KEY\ntime_limits")]
    end

    CLIENT(["👤 Cliente HTTP"]) -- "HTTPS POST /otimizar\nX-API-Key" --> API
    API --> AUTH
    AUTH -- "403 se inválida" --> CLIENT
    API --> SCHEMA
    SCHEMA -- "422 se inválido" --> CLIENT
    API --> SOLVER
    SOLVER -- "OptimizationResponse" --> API
    API -- "200 OK + plano_corte" --> CLIENT
    CONFIG --> ENV
    AUTH --> CONFIG
    SOLVER --> CONFIG
```

## 3. Mapa de bounded contexts (DDD)

```mermaid
flowchart LR
    subgraph BC_OT["Otimização de Corte (core)"]
        direction TB
        EP["POST /otimizar"]
        SOLVE["resolver_corte()"]
        EP --> SOLVE
    end

    subgraph BC_AUTH["Autenticação (supporting)"]
        AK["verify_api_key()"]
    end

    subgraph BC_CFG["Configuração (generic)"]
        CFG["Settings (pydantic-settings)"]
    end

    BC_AUTH -- "Customer/Supplier\n(decide: 403 ou prosseguir)" --> BC_OT
    BC_CFG -- "Shared Kernel\n(settings.api_key, time_limits)" --> BC_AUTH
    BC_CFG -- "Shared Kernel\n(settings.solver_default_time_limit)" --> BC_OT
```

## 4. Fluxo de uma requisição de otimização (Sequence)

```mermaid
sequenceDiagram
    participant C as Cliente HTTP
    participant A as api.py (FastAPI)
    participant AU as auth.py
    participant S as schemas.py
    participant SO as solver.py (OR-Tools)

    C->>A: POST /otimizar + X-API-Key + JSON body
    A->>AU: verify_api_key(x_api_key)
    alt chave ausente ou incorreta
        AU-->>A: raise HTTPException(403)
        A-->>C: 403 Forbidden
    end
    AU-->>A: api_key válida

    A->>S: OptimizationRequest(**body)
    alt payload inválido
        S-->>A: ValidationError
        A-->>C: 422 Unprocessable Entity
    end
    S-->>A: OptimizationRequest validado

    A->>SO: resolver_corte(comprimento_padrao, itens, time_limit)
    SO->>SO: CpModel() + variáveis y[j], x[i][j]
    SO->>SO: restrições + objetivo + CpSolver.solve(time_limit)
    SO-->>A: OptimizationResponse (OPTIMAL/FEASIBLE/INFEASIBLE)

    A-->>C: 200 OK + OptimizationResponse (JSON)
```

## 5. Estrutura de arquivos (referência rápida)

```mermaid
graph TD
    ROOT["OptimizationAAService/"] --> SRC["src/"]
    ROOT --> TESTS["tests/"]
    ROOT --> SPECS["specs/0001-api-otimizacao/"]
    ROOT --> DOCS["docs/"]
    ROOT --> CFG_FILES["render.yaml · requirements.txt · .env.example"]

    SRC --> API["api.py — FastAPI endpoints"]
    SRC --> AUTH["auth.py — API Key auth"]
    SRC --> SCHEMA["schemas.py — Pydantic v2"]
    SRC --> SOLVER["solver.py — OR-Tools"]
    SRC --> CONFIG["config.py — pydantic-settings"]

    TESTS --> TS["test_solver.py (16 testes)"]
    TESTS --> TA["test_api.py (18 testes)"]

    SPECS --> SPEC["spec.md — 12 ACs"]
    SPECS --> DESIGN["design.md — TDD"]
    SPECS --> TASKS["tasks.md — 11 tasks"]
    SPECS --> PRODUCT["product.md"]
    SPECS --> DOMAIN["domain.md"]

    DOCS --> ARCH["architecture/"]
    ARCH --> ADR["adr/ — 0002, 0003, 0004"]
    ARCH --> OVW["overview.md"]
    ARCH --> CTX["context-map.md"]
    ARCH --> DGR["diagrams.md"]
```
