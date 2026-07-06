---
name: product
description: Contexto de negócio — por quê e para quem. Consulte ao priorizar escopo.
alwaysApply: false
---

# Product — API de Otimização para o Corte Unidimensional

## Por quê

Empresas que cortam materiais lineares (aço, madeira, vidro, cabos) geram desperdício
significativo quando o planejamento de corte é feito manualmente ou por heurísticas simples.
Este serviço disponibiliza o solver de Kantorovich via API REST para qualquer sistema poder
calcular o plano de corte ótimo sem precisar hospedar a lógica de otimização localmente.

## Para quem

- **Estudantes e professores** de Pesquisa Operacional e Ciências de Dados (contexto da UFC)
- **Desenvolvedores** que precisam integrar otimização de corte em ERPs, WMS ou sistemas industriais
- **Pesquisadores** que querem um oráculo de referência para validar heurísticas próprias

## Métricas de sucesso

| Métrica                              | Meta inicial             |
|--------------------------------------|--------------------------|
| Disponibilidade (uptime)             | ≥ 99% no Render          |
| Tempo de resposta p95 (instâncias pequenas) | < 5s              |
| Cobertura de testes automatizados    | ≥ 80% de linhas          |
| Nota na rubrica da disciplina        | 10/10                    |

## MVP — o que este projeto entrega

1. `GET /health` — liveness probe
2. `POST /otimizar` — solve do problema de corte com OR-Tools
3. Autenticação por API Key (`X-API-Key`)
4. Validação rigorosa de entrada (Pydantic v2)
5. Limite de tempo do solver configurável (1–120s, padrão 60s)
6. Documentação Swagger (`/docs`) rica com exemplos
7. Deploy público no Render com URL no topo do README
8. Suíte de ≥ 10 testes automatizados com pytest
