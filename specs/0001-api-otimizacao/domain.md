---
name: domain
description: Linguagem ubíqua e modelo do domínio de corte unidimensional. Consulte ao nomear código.
alwaysApply: false
---

# Domain — Corte Unidimensional

## Linguagem ubíqua

Estes termos devem ser usados **identicamente** no código, na spec, nos testes e na conversa
com o time. Não invente sinônimos.

| Termo (PT)              | Termo em código (`snake_case`) | Definição                                                                 |
|-------------------------|-------------------------------|---------------------------------------------------------------------------|
| Barra padrão            | `barra_padrao`                | Unidade de matéria-prima de comprimento fixo *L* disponível em estoque   |
| Comprimento padrão      | `comprimento_padrao`          | Comprimento útil de cada barra padrão em estoque (parâmetro *L*)          |
| Item de demanda         | `item`                        | Subpeça de comprimento *lᵢ* requerida em quantidade *dᵢ*                 |
| Demanda                 | `quantidade`                  | Número de unidades do item requeridas (*dᵢ*)                             |
| Plano de corte          | `plano_corte`                 | Conjunto de instruções indicando quais itens cortar de cada barra         |
| Padrão de corte         | `itens_cortados`              | Lista de itens (e quantidades) extraídos de uma barra específica          |
| Desperdício             | `sobra`                       | Comprimento remanescente não utilizado após os cortes em uma barra        |
| Desperdício total       | `desperdicio_total_mm`        | Soma das sobras de todas as barras utilizadas                             |
| Status do solver        | `status_solver`               | Resultado do processo de otimização: OPTIMAL, FEASIBLE ou INFEASIBLE      |
| Tempo limite            | `time_limit`                  | Tempo máximo (segundos) para o solver buscar a solução                   |
| Tempo de execução       | `tempo_execucao_segundos`     | Tempo real gasto pelo solver para encontrar a solução                    |

## Modelo do domínio

```
OptimizationRequest
├── comprimento_padrao: int  (L > 0, em mm)
├── itens: List[Item]        (len >= 1)
│   ├── id: str
│   ├── comprimento: int     (0 < lᵢ ≤ L)
│   └── quantidade: int      (dᵢ > 0)
└── time_limit: Optional[int] (1 ≤ t ≤ 120, default=60)

OptimizationResult
├── status_solver: str       ("OPTIMAL" | "FEASIBLE" | "INFEASIBLE")
├── tempo_execucao_segundos: float
├── barras_utilizadas: int
├── desperdicio_total_mm: int
└── plano_corte: List[Barra]
    ├── barra_id: int
    ├── itens_cortados: List[ItemCortado]
    │   ├── item_id: str
    │   └── quantidade: int
    ├── comprimento_utilizado: int
    └── sobra: int

# Invariante: comprimento_utilizado + sobra == comprimento_padrao
# Invariante: sum(itens_cortados[i].comprimento * itens_cortados[i].quantidade) == comprimento_utilizado
```

## Formulação matemática (referência)

**Minimize** Z = Σⱼ yⱼ

**Sujeito a:**
- Σⱼ xᵢⱼ ≥ dᵢ, ∀i (atende demanda)
- Σᵢ lᵢ · xᵢⱼ ≤ L · yⱼ, ∀j (respeita comprimento da barra)
- yⱼ ∈ {0, 1}, xᵢⱼ ∈ ℤ≥₀

Onde N = Σᵢ dᵢ é o upper bound do número de barras.
