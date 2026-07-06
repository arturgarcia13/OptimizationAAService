---
name: context-map
description: Bounded contexts e relações. Puxe ao modelar ou cruzar contextos.
alwaysApply: false
---

# Context Map — Optimization-as-a-Service

> Visão DDD estratégica: os bounded contexts do sistema e como se relacionam.
> Atualize quando uma feature cria/move fronteiras.

## Bounded Contexts

| Contexto                  | Subdomínio           | Responsabilidade                                                         | Dono           |
|---------------------------|----------------------|--------------------------------------------------------------------------|----------------|
| **Otimização de Corte**   | core                 | Receber requisições de corte, resolver via OR-Tools, retornar plano ótimo | Equipe UFC     |
| **Autenticação**          | supporting           | Validar API Keys e controlar acesso às rotas protegidas                  | Equipe UFC     |
| **Configuração**          | generic              | Ler variáveis de ambiente e fornecer settings tipados para o sistema     | Equipe UFC     |

> **Nota de escopo:** o projeto é um **single-service** (micromonolito) com 3 responsabilidades
> internas distintas. Não há comunicação com sistemas externos além do OR-Tools (biblioteca local).
> A divisão em contextos reflete a separação de responsabilidade dos módulos, não deploys separados.

## Relações entre contextos

```
[Autenticação] ──(Customer/Supplier)──► [Otimização de Corte]
                                                │
[Configuração] ────────────────────────────────►│
```

| Upstream             | Downstream             | Padrão              | Por quê                                                         |
|----------------------|------------------------|---------------------|-----------------------------------------------------------------|
| Autenticação         | Otimização de Corte    | Customer/Supplier   | O contexto de corte consome a decisão de auth (403 vs prosseguir) |
| Configuração         | Otimização de Corte    | Shared Kernel       | Settings (time_limit, API_KEY) são consumidos por ambos       |
| Configuração         | Autenticação           | Shared Kernel       | `settings.api_key` é lido pelo contexto de autenticação        |

## Sistemas externos

| Sistema           | Tipo           | Interação                                                   |
|-------------------|----------------|-------------------------------------------------------------|
| OR-Tools (CP-SAT) | Biblioteca local| O contexto de Otimização chama `cp_model.CpSolver.solve()` |
| Render            | Plataforma IaaS | Hospeda o container; lê variáveis de ambiente              |
| Cliente HTTP      | Ator externo   | Envia `POST /otimizar` com payload e `X-API-Key`           |

## Diagramas

Os diagramas de arquitetura (C4 e fluxo de requisição) estão em
[`diagrams.md`](./diagrams.md).
