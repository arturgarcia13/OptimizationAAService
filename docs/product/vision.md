---
name: vision
description: Visão do produto. Consulte ao priorizar escopo ou definir o MVP.
alwaysApply: false
---

# Visão do produto — Optimization-as-a-Service

> **Working backwards (Amazon):** começar pelo cliente e pelo resultado desejado,
> não pela tecnologia. Responde: *por que existe e para quem?*

## Declaração de visão

**Para** desenvolvedores, pesquisadores e estudantes de Pesquisa Operacional
**que precisam** de um solver acessível de Corte Unidimensional sem hospedar
a lógica de otimização localmente,

**a** Optimization-as-a-Service **é uma** API REST pública e gratuita

**que** recebe uma descrição do problema (barra padrão + lista de itens) e retorna
o plano de corte ótimo calculado pelo Google OR-Tools, via simples chamada HTTP.

**Diferente de** soluções comerciais (Gurobi, CPLEX) ou implementações locais,
nosso produto **é gratuito, sem instalação, com documentação interativa (Swagger)
e contrato JSON bem definido**.

## Personas

### P1 — Estudante de Pesquisa Operacional (persona primária)

- **Contexto:** cursando disciplina de Laboratório de Otimização na UFC
- **Objetivo:** validar implementações próprias de heurísticas comparando com o ótimo
- **Dor:** configurar OR-Tools localmente tem curva de aprendizado; quer um oráculo rápido
- **Como usa:** envia `POST /otimizar` via Swagger UI ou script Python

### P2 — Desenvolvedor de software industrial

- **Contexto:** desenvolve ERP ou WMS para indústria metalúrgica/madeireira
- **Objetivo:** integrar cálculo ótimo de corte sem manter solver próprio
- **Dor:** solver comercial caro; instância cloud dedicada custosa para demanda baixa
- **Como usa:** integra via REST; usa API Key para autenticar; consome JSON estruturado

### P3 — Pesquisador acadêmico

- **Contexto:** desenvolve novas heurísticas ou metaheurísticas para o 1D-CSP
- **Objetivo:** comparar resultados com o ótimo exato do MIP de Kantorovich
- **Dor:** reimplementar o solver para cada experimento consome tempo
- **Como usa:** chama via script de pesquisa; usa `time_limit` para controlar o benchmark

## Métricas de sucesso

| Métrica                           | Meta inicial      | Como medir                             |
|-----------------------------------|-------------------|----------------------------------------|
| Nota na rubrica da disciplina     | 10/10             | Rubrica do projeto_final.md            |
| Cobertura de testes               | ≥ 80%             | pytest-cov (atual: 97%)                |
| Disponibilidade (uptime)          | ≥ 99%             | Render health check monitoring         |
| Tempo de resposta p95             | < 5s para N < 50  | `tempo_execucao_segundos` na resposta  |
| API funcional e documentada       | ✅ no deploy       | GET /docs retorna 200                  |

## MVP — o que é entregue na Onda 1

1. `GET /health` — liveness probe
2. `POST /otimizar` — resolve o problema de corte com OR-Tools / Kantorovich
3. Autenticação por API Key (`X-API-Key`)
4. Validação rigorosa de entrada (Pydantic v2) com mensagens úteis
5. Limite de tempo do solver configurável (1–120s, padrão 60s)
6. Documentação Swagger (`/docs`) rica com exemplos e tags
7. Deploy público no Render com URL no topo do README
8. Suíte de ≥ 10 testes automatizados com pytest (entregue: 34)

## O que NÃO está no MVP (fora de escopo)

- Frontend/interface web de visualização
- Persistência de histórico de requisições
- Rate limiting por cliente
- Corte bidimensional ou tridimensional
- JWT / OAuth2
- Múltiplos comprimentos padrão de barra por requisição
