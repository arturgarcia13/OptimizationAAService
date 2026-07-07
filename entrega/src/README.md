---
name: src
description: Mapeamento de camadas DDD no código do projeto. Puxe ao estruturar ou implementar código.
alwaysApply: false
---

# src/ — Mapeamento de camadas no projeto

> Este projeto é um **monolito modular de arquivo único por responsabilidade**.
> Os módulos se mapeiam para as camadas DDD conforme abaixo.
> A **regra de dependência** é preservada: as setas apontam só para dentro.

```
interfaces (api.py) ──► application (solver.py) ──► domain (schemas.py) ◄── infrastructure (config.py)
```

## Mapeamento de camadas → arquivos

| Camada DDD      | Arquivo         | Responsabilidade                                                    | Pode depender de       |
|-----------------|-----------------|---------------------------------------------------------------------|------------------------|
| `domain`        | `schemas.py`    | Modelos Pydantic v2, validações, invariantes de negócio             | **nada** do projeto    |
| `application`   | `solver.py`     | Orquestra o caso de uso: monta o modelo CP-SAT e retorna o resultado| `schemas.py`           |
| `infrastructure`| `config.py`     | Lê variáveis de ambiente via pydantic-settings                      | **nada** do projeto    |
| `interfaces`    | `api.py`        | FastAPI: endpoints HTTP, dependency injection, serialização         | `solver.py`, `auth.py`, `schemas.py`, `config.py` |
| `interfaces`    | `auth.py`       | Dependency de autenticação (API Key). Parte da borda de entrada     | `config.py`            |

## Por que essa estrutura é correta

- **schemas.py** não importa nada de `fastapi`, `ortools` ou `config` — é **domínio puro**
- **solver.py** não importa nada de `fastapi` ou `config` — **testável isoladamente**
- **config.py** não importa nada do projeto — **infraestrutura pura**
- **api.py** é a única camada que conhece FastAPI — **borda isolada**

## Regra anti-violação (ao adicionar código)

> ❌ `schemas.py` importando `fastapi` → viola domínio puro
> ❌ `solver.py` importando `api` → viola dependência
> ❌ `config.py` importando `solver` ou `schemas` → viola infraestrutura
> ✅ `api.py` importando qualquer outra camada → permitido (é a borda)

## Por que não há subpastas domain/, application/, etc.

O projeto é **pequeno** (< 300 linhas de código produtivo) e a separação por arquivo
cumpre o mesmo objetivo de separação de responsabilidades com **menos complexidade acidental**
(KISS — Hooker). Quando o projeto crescer para a Onda 3 (novos bounded contexts),
migre para subpastas sem quebrar a regra de dependência.
