---
name: ADR-0003
description: OR-Tools com formulação de Kantorovich para o solver
alwaysApply: false
---

# ADR-0003: OR-Tools com formulação de Kantorovich para o solver de corte unidimensional

**Data:** 2026-07-06
**Status:** Aceito
**Autores:** Equipe do projeto

## Contexto

O solver de otimização precisa resolver o Problema de Corte Unidimensional. A spec (AC-2)
exige que o resultado seja ótimo (ou melhor factível dentro do time_limit). O enunciado
do projeto já especifica OR-Tools e a formulação de Kantorovich.

## Decisão

Utilizamos o **Google OR-Tools** (biblioteca `ortools`) com a formulação de **programação
inteira mista de Kantorovich**:

- Variáveis binárias `y[j]`: indica se a barra `j` foi usada
- Variáveis inteiras `x[i][j]`: quantidade do item `i` cortada da barra `j`
- Objetivo: minimizar Σ yⱼ (número de barras usadas)
- Restrições: demanda suprida + capacidade de cada barra respeitada
- Upper bound N = Σ dᵢ (caso extremo: uma barra por unidade)

## Alternativas consideradas

| Abordagem                     | Prós                                  | Contras                                          |
|-------------------------------|---------------------------------------|--------------------------------------------------|
| OR-Tools / Kantorovich (MIP)  | Solução ótima garantida, OR-Tools é gratuito e Python-nativo | Pode ser lento para instâncias grandes |
| Heurística (First Fit Decreasing) | Muito rápido                     | Não garante ótimo                               |
| Column Generation (Gilmore-Gomory) | Escala melhor para instâncias grandes | Muito mais complexo de implementar          |

## Consequências

- **Positivas:** Solução ótima para instâncias de tamanho típico (< 100 itens), fácil integração com Python.
- **Negativas:** Para instâncias com N muito grande (ex: 1000+ barras), o MIP pode ser lento — mitigado pelo `time_limit`.
- **Mitigação:** O `time_limit` (padrão 60s, máximo 120s) garante que o solver sempre retorne, mesmo que com solução FEASIBLE em vez de OPTIMAL.
