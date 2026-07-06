---
name: glossary
description: Linguagem ubíqua do sistema. Puxe ao nomear, modelar domínio ou escrever specs.
alwaysApply: false
---

# Glossário — Linguagem Ubíqua

> A fonte única do vocabulário do sistema. O mesmo termo aparece aqui, na spec e no código.
> Termo novo introduzido por uma feature → adicione no mesmo PR. Sem sinônimos.

| Termo (`snake_case` em código)     | Definição precisa no domínio                                                        | NÃO confundir com                        | Contexto               |
|------------------------------------|-------------------------------------------------------------------------------------|------------------------------------------|------------------------|
| `barra_padrao`                     | Unidade de matéria-prima de comprimento fixo *L* disponível em estoque              | barra já cortada                         | Otimização de Corte    |
| `comprimento_padrao`               | Comprimento útil de cada barra padrão em estoque (parâmetro *L*, em mm)             | comprimento de um item                   | Otimização de Corte    |
| `item`                             | Subpeça de comprimento *lᵢ* requerida em quantidade *dᵢ* (item de demanda)         | produto final                            | Otimização de Corte    |
| `comprimento` (de item)            | Comprimento necessário do item *i* em milímetros (*lᵢ*). Deve ser ≤ *L*           | comprimento total da barra               | Otimização de Corte    |
| `quantidade`                       | Demanda total exigida do item *i* (*dᵢ*). Deve ser > 0                             | quantidade já produzida                  | Otimização de Corte    |
| `plano_corte`                      | Conjunto de instruções indicando quais itens cortar de cada barra padrão            | orçamento, pedido                        | Otimização de Corte    |
| `itens_cortados`                   | Lista de itens (e quantidades) extraídos de uma barra específica                    | itens do pedido                          | Otimização de Corte    |
| `sobra`                            | Comprimento remanescente não utilizado após os cortes em uma barra (mm)             | refugo, peça                             | Otimização de Corte    |
| `desperdicio_total_mm`             | Soma das sobras de todas as barras utilizadas (mm)                                  | custo de material                        | Otimização de Corte    |
| `status_solver`                    | Resultado do processo de otimização: `OPTIMAL`, `FEASIBLE` ou `INFEASIBLE`         | status HTTP                              | Otimização de Corte    |
| `OPTIMAL`                          | Solver encontrou a solução matematicamente ótima dentro do time_limit               | melhor encontrado (FEASIBLE)             | Otimização de Corte    |
| `FEASIBLE`                         | Solver encontrou uma solução válida mas possivelmente não ótima (esgotou time_limit)| solução sem garantia de qualidade        | Otimização de Corte    |
| `INFEASIBLE`                       | Solver provou que não existe solução para o problema dado (impossível)              | timeout, erro                            | Otimização de Corte    |
| `time_limit`                       | Tempo máximo em segundos que o solver pode usar antes de retornar (1–120s, padrão 60s) | timeout HTTP da requisição           | Otimização de Corte    |
| `tempo_execucao_segundos`          | Tempo real medido pelo solver para encontrar a solução (float, em segundos)         | time_limit (máximo configurado)          | Otimização de Corte    |
| `barras_utilizadas`                | Número total de barras padrão que aparecem no plano de corte                        | barras disponíveis em estoque            | Otimização de Corte    |
| `barra_id`                         | Identificador sequencial de uma barra no plano de corte (começa em 1)              | ID de produto em catálogo                | Otimização de Corte    |
| `comprimento_utilizado`            | Soma dos comprimentos efetivamente cortados nessa barra (mm). Invariante: + sobra = L | comprimento do item                   | Otimização de Corte    |
| `API Key`                          | Token estático compartilhado enviado no cabeçalho `X-API-Key` para autenticar       | JWT, OAuth token, session cookie         | Segurança              |
| `X-API-Key`                        | Nome do cabeçalho HTTP que carrega a API Key                                        | Authorization (Bearer)                   | Segurança              |
| Formulação de Kantorovich          | Modelo MIP com variáveis binárias *yⱼ* (barra usada) e inteiras *xᵢⱼ* (quantidade do item *i* na barra *j*) | column generation (Gilmore-Gomory) | Solver / Matemática |
| CP-SAT                             | Constraint Programming + SAT: engine do OR-Tools usado como solver                  | LP, Gurobi, CPLEX                        | Solver / Matemática    |
| Upper bound N                      | Limite superior do número de barras = Σdᵢ (pior caso: uma barra por unidade)      | número ótimo de barras                   | Solver / Matemática    |
| cold start                         | Atraso (~30s) ao acordar uma instância do Render após inatividade                   | lentidão do solver                       | Operacional / Infra    |

<!-- Mantido em ordem alfabética aproximada por contexto. Cada linha tem um dono mental claro. -->
