---
name: spec
description: Contrato da API de Otimização (critérios de aceite). Fonte da verdade.
alwaysApply: true
---

# Spec — API de Otimização para o Corte Unidimensional

> **Fonte da verdade.** Status: aprovado
> Os critérios de aceite são (a) o contrato com o negócio, (b) o oráculo de teste,
> (c) o prompt para o agente de IA implementar. Escritos para serem executáveis.

## Resumo

O sistema expõe uma API REST que, dado um comprimento padrão de barra e uma lista de itens
com seus comprimentos e quantidades, resolve o Problema de Corte Unidimensional usando
Google OR-Tools (formulação de Kantorovich) e retorna o plano de corte ótimo (ou melhor
factível), minimizando o número de barras utilizadas.

## Critérios de aceite

### AC-1: Endpoint de health-check
- **Dado** que a API esteja em execução
- **Quando** um cliente faz `GET /health`
- **Então** a resposta tem status `200 OK` e corpo `{"status": "ok"}`

### AC-2: Otimização com solução ótima
- **Dado** um payload válido com `comprimento_padrao=3000`, `itens=[{id:"A",comprimento:1150,quantidade:3},{id:"B",comprimento:800,quantidade:4},{id:"C",comprimento:450,quantidade:5}]` e API Key correta no cabeçalho `X-API-Key`
- **Quando** o cliente faz `POST /otimizar`
- **Então** a resposta tem status `200 OK`, `status_solver="OPTIMAL"`, `barras_utilizadas` é um inteiro positivo, `desperdicio_total_mm >= 0`, e `plano_corte` contém pelo menos uma barra com seus `itens_cortados`, `comprimento_utilizado` e `sobra`

### AC-3: Validação Pydantic — comprimento_padrao inválido
- **Dado** um payload com `comprimento_padrao=0` (ou negativo, ou ausente)
- **Quando** o cliente faz `POST /otimizar`
- **Então** a resposta tem status `422 Unprocessable Entity` com detalhe do campo inválido

### AC-4: Validação Pydantic — item com comprimento maior que a barra
- **Dado** um payload com `comprimento_padrao=1000` e um item com `comprimento=1500`
- **Quando** o cliente faz `POST /otimizar`
- **Então** a resposta tem status `422 Unprocessable Entity` indicando que o item excede o comprimento padrão

### AC-5: Validação Pydantic — demanda não positiva
- **Dado** um payload com algum item com `quantidade=0` (ou negativo)
- **Quando** o cliente faz `POST /otimizar`
- **Então** a resposta tem status `422 Unprocessable Entity`

### AC-6: Segurança — requisição sem API Key
- **Dado** um payload válido mas sem o cabeçalho `X-API-Key`
- **Quando** o cliente faz `POST /otimizar`
- **Então** a resposta tem status `403 Forbidden`

### AC-7: Segurança — requisição com API Key inválida
- **Dado** um payload válido mas com `X-API-Key` com valor incorreto
- **Quando** o cliente faz `POST /otimizar`
- **Então** a resposta tem status `403 Forbidden`

### AC-8: Confiabilidade — time_limit padrão
- **Dado** um payload válido sem o campo `time_limit`
- **Quando** o cliente faz `POST /otimizar`
- **Então** o solver roda com tempo máximo de 60 segundos e retorna resultado dentro desse limite

### AC-9: Confiabilidade — time_limit customizado válido
- **Dado** um payload válido com `time_limit=30` (segundos, entre 1 e 120)
- **Quando** o cliente faz `POST /otimizar`
- **Então** o solver respeita o limite customizado e retorna o melhor resultado encontrado até então

### AC-10: Confiabilidade — time_limit excedendo o máximo
- **Dado** um payload com `time_limit=200` (acima do máximo de 120s)
- **Quando** o cliente faz `POST /otimizar`
- **Então** a resposta tem status `422 Unprocessable Entity` indicando que o valor excede o máximo

### AC-11: Documentação Swagger disponível
- **Dado** que a API esteja em execução
- **Quando** um cliente acessa `GET /docs`
- **Então** a interface Swagger UI é exibida com todos os endpoints documentados

### AC-12: Proteção de tracebacks em produção
- **Dado** que ocorra um erro interno não tratado
- **Quando** a API retorna a resposta de erro
- **Então** o corpo da resposta NÃO expõe stack trace completo da aplicação (apenas mensagem genérica)

## Matriz de decisão — Cenários de autenticação

| X-API-Key presente | Valor correto | Resultado esperado         | AC    |
|--------------------|---------------|----------------------------|-------|
| Não                | —             | 403 Forbidden              | AC-6  |
| Sim                | Não           | 403 Forbidden              | AC-7  |
| Sim                | Sim           | Processamento normal       | AC-2  |

## Casos de borda e erros

- Lista `itens` vazia → `422 Unprocessable Entity`
- `comprimento` de item igual ao da barra → válido (zero de sobra por item)
- `time_limit=0` → `422` (deve ser > 0)
- `time_limit=120` → válido (limite máximo aceito)
- `time_limit=121` → `422` (excede máximo)
- Solver retorna `INFEASIBLE` → `200 OK` com `status_solver="INFEASIBLE"` e plano vazio
- Solver excede o tempo → `200 OK` com `status_solver="FEASIBLE"` e melhor solução parcial

## Fora de escopo

> Vinculante. Não implemente nada aqui.
- Corte bidimensional ou multidimensional
- Persistência de histórico de requisições em banco de dados
- Rate limiting por cliente
- Autenticação JWT / OAuth2
- Interface web (frontend) de visualização
- Múltiplos comprimentos padrão de barra numa única requisição

## Rastreabilidade

- Product: `./product.md`
- Design: `./design.md`
- Domínio: `./domain.md`
- ADRs relacionados:
  - [ADR-0002: API Key como mecanismo de autenticação](../../docs/architecture/adr/0002-api-key-auth.md)
  - [ADR-0003: OR-Tools com formulação de Kantorovich](../../docs/architecture/adr/0003-ortools-kantorovich.md)
  - [ADR-0004: Render como plataforma de deploy](../../docs/architecture/adr/0004-render-deploy.md)
