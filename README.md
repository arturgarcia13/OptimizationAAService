---
name: README
description: Manual de instalação, formulação e uso da API. 
alwaysApply: fals
---

# API de Otimização — Corte Unidimensional (1D Cutting Stock Problem)

> **🌐 URL Pública:** `https://optimization-aa-service.onrender.com`
>
> **Swagger UI (interativo):** [`https://optimization-aa-service.onrender.com/docs`](https://optimization-aa-service.onrender.com/docs)
>
> ⚠️ **Nota (cold start):** o free tier do Render "adormece" após 15 min de inatividade.
> O primeiro request pode levar ~30s. Aguarde e tente novamente se receber timeout.

---

Projeto Final da Disciplina **Laboratório de Otimização — Ciências de Dados**
Universidade Federal do Ceará — 2026.1

---

## 🎯 O Problema

O **Problema de Corte Unidimensional** (*1D Cutting Stock Problem*) é um clássico de
Pesquisa Operacional aplicado em indústrias que cortam materiais lineares (aço, madeira,
vidro, cabos). O objetivo é determinar como cortar barras padrão de comprimento *L* para
satisfazer a demanda de itens menores *lᵢ* com quantidade *dᵢ*, **minimizando o número
total de barras usadas** (equivalente a minimizar o desperdício).

### Formulação Matemática (Kantorovich)

**Conjuntos:**
- *i ∈ {1,…,m}*: índice dos itens de demanda
- *j ∈ {1,…,N}*: índice das barras (N = Σdᵢ — upper bound)

**Parâmetros:**
- *L*: comprimento útil da barra padrão (mm)
- *lᵢ*: comprimento do item *i* (mm)
- *dᵢ*: demanda do item *i* (unidades)

**Variáveis de decisão:**
- *yⱼ ∈ {0,1}*: 1 se a barra *j* é utilizada
- *xᵢⱼ ∈ ℤ≥₀*: quantidade do item *i* cortada na barra *j*

**Modelo:**

```
Minimizar   Z = Σⱼ yⱼ

Sujeito a:
  Σⱼ xᵢⱼ ≥ dᵢ,        ∀i  — demanda atendida
  Σᵢ lᵢ·xᵢⱼ ≤ L·yⱼ,   ∀j  — capacidade da barra respeitada
  yⱼ ∈ {0,1},          ∀j
  xᵢⱼ ∈ ℤ≥₀,           ∀i,j
```

---

## 🚀 Instalação e execução local

### Pré-requisitos

- Python 3.11 ou 3.12
- Git

### 1. Clone o repositório

```bash
git clone https://github.com/<seu-usuario>/OptimizationAAService.git
cd OptimizationAAService
```

### 2. Crie e ative o ambiente virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` e defina sua `API_KEY`:

```env
API_KEY=sua-chave-secreta-aqui
```

> Gere uma chave segura com:
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 5. Execute a API

```bash
uvicorn src.api:app --reload
```

A API estará disponível em `http://localhost:8000`.
Documentação interativa: `http://localhost:8000/docs`.

---

## 🔐 Autenticação

Todos os endpoints de otimização exigem o cabeçalho `X-API-Key`:

```http
POST /otimizar HTTP/1.1
Content-Type: application/json
X-API-Key: sua-chave-aqui
```

Requisições sem chave ou com chave inválida retornam **403 Forbidden**.

---

## 📋 Endpoints

### `GET /health`

Verifica se a API está operacional. **Não requer autenticação.**

```bash
curl http://localhost:8000/health
```

Resposta:
```json
{"status": "ok"}
```

---

### `POST /otimizar`

Resolve o Problema de Corte Unidimensional. **Requer autenticação.**

**Exemplo de requisição:**
```bash
curl -X POST http://localhost:8000/otimizar \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave-aqui" \
  -d '{
    "comprimento_padrao": 3000,
    "itens": [
      {"id": "item_A", "comprimento": 1150, "quantidade": 3},
      {"id": "item_B", "comprimento": 800,  "quantidade": 4},
      {"id": "item_C", "comprimento": 450,  "quantidade": 5}
    ]
  }'
```

**Resposta (200 OK):**
```json
{
  "status_solver": "OPTIMAL",
  "tempo_execucao_segundos": 0.045,
  "barras_utilizadas": 4,
  "desperdicio_total_mm": 3100,
  "plano_corte": [
    {
      "barra_id": 1,
      "itens_cortados": [{"item_id": "item_A", "quantidade": 2}],
      "comprimento_utilizado": 2300,
      "sobra": 700
    },
    ...
  ]
}
```

**Parâmetros de entrada:**

| Campo               | Tipo          | Obrigatório | Descrição                                           |
|---------------------|---------------|-------------|-----------------------------------------------------|
| `comprimento_padrao`| `int > 0`     | ✅           | Comprimento útil da barra em mm                     |
| `itens`             | `List[Item]`  | ✅           | Lista de itens de demanda (mín. 1 item)             |
| `itens[].id`        | `str`         | ✅           | Identificador único do item                         |
| `itens[].comprimento`| `int > 0`   | ✅           | Comprimento do item em mm (deve ser ≤ barra padrão) |
| `itens[].quantidade`| `int > 0`     | ✅           | Quantidade demandada do item                        |
| `time_limit`        | `int [1,120]` | ❌           | Limite de tempo do solver em segundos (padrão: 60)  |

**Campos da resposta:**

| Campo                    | Tipo            | Descrição                                        |
|--------------------------|-----------------|--------------------------------------------------|
| `status_solver`          | `str`           | `OPTIMAL`, `FEASIBLE` ou `INFEASIBLE`            |
| `tempo_execucao_segundos`| `float`         | Tempo real gasto pelo solver                     |
| `barras_utilizadas`      | `int`           | Número de barras padrão no plano de corte        |
| `desperdicio_total_mm`   | `int`           | Soma das sobras de todas as barras               |
| `plano_corte`            | `List[Barra]`   | Detalhamento por barra                           |

**Códigos de resposta:**

| Código | Significado                                          |
|--------|------------------------------------------------------|
| 200    | Otimização concluída com sucesso                     |
| 403    | API Key ausente ou inválida                          |
| 422    | Parâmetros de entrada inválidos (detalhe no corpo)   |
| 500    | Erro interno do servidor                             |

---

## 🧪 Executar os testes

```bash
# Todos os testes (mínimo 10 testes distintos)
pytest

# Com relatório de cobertura
pytest --cov=src --cov-report=term-missing

# Apenas testes unitários do solver
pytest tests/test_solver.py -v

# Apenas testes de integração da API
pytest tests/test_api.py -v
```

> **Nota:** antes de rodar os testes, certifique-se de que o `.env` existe com
> `API_KEY=test-api-key-segura-12345` (o `test_api.py` usa esse valor padrão via `os.environ.setdefault`).

---

## 📁 Estrutura do projeto

```
OptimizationAAService/
├── src/
│   ├── api.py          # Configuração FastAPI e endpoints
│   ├── schemas.py      # Validadores Pydantic de entrada e saída
│   ├── auth.py         # Controle de acesso (API Key)
│   ├── solver.py       # Modelagem matemática (OR-Tools / Kantorovich)
│   └── config.py       # Configurações e variáveis de ambiente
├── tests/
│   ├── test_solver.py  # Testes unitários do modelo matemático (≥10)
│   └── test_api.py     # Testes de integração das rotas (≥10)
├── specs/
│   └── 0001-api-otimizacao/  # Esteira SDD: spec, tasks, product, domain
├── docs/architecture/adr/    # ADRs: decisões arquiteturais duráveis
├── .env.example        # Template de variáveis de ambiente
├── .gitignore          # .env bloqueado (segredos protegidos)
├── requirements.txt    # Dependências Python
├── pytest.ini          # Configuração do pytest
├── render.yaml         # Configuração declarativa do deploy no Render
└── api_requests.http   # Exemplos de requisições para teste manual
```

---

## 🌐 Deploy (Render)

1. Faça fork do repositório e conecte ao Render
2. O Render detecta automaticamente o `render.yaml`
3. Configure a variável `API_KEY` no painel:
   **Dashboard → Service → Environment → Add Environment Variable**
4. O deploy é automático a cada push na branch `main`

---

## 🛡️ Segurança

- `API_KEY` armazenada apenas em variáveis de ambiente (nunca commitada)
- `.env` bloqueado pelo `.gitignore`
- Tracebacks internos ocultados em produção (AC-12)
- Limites estritos no `time_limit` do solver (1–120s) evitam abuso de recursos

---

## 📚 Tecnologias

| Tecnologia          | Versão   | Uso                                    |
|---------------------|----------|----------------------------------------|
| Python              | 3.12     | Linguagem principal                    |
| FastAPI             | 0.115    | Framework web REST                     |
| Pydantic v2         | 2.10     | Validação de schemas                   |
| Google OR-Tools     | 9.11     | Solver de otimização (CP-SAT)          |
| uvicorn             | 0.32     | Servidor ASGI                          |
| pytest              | 8.3      | Testes automatizados                   |
| Render              | —        | Hospedagem (free tier)                 |

---

*Laboratório de Otimização — Ciências de Dados — UFC 2026.1*
