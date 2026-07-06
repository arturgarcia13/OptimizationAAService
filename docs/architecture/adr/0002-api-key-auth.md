# ADR-0002: API Key como mecanismo de autenticação da rota de otimização

**Data:** 2026-07-06
**Status:** Aceito
**Autores:** Equipe do projeto

## Contexto

A spec (AC-6, AC-7) exige que a rota `POST /otimizar` seja protegida contra requisições não
autorizadas. O `projeto_final.md` (seção 3.4) oferece duas opções: (A) API Key via cabeçalho
`X-API-Key` ou (B) JWT com endpoint `/auth/login`.

## Decisão

Adotamos a **Opção A: API Key** validada via cabeçalho `X-API-Key` contra o valor armazenado
na variável de ambiente `API_KEY` (arquivo `.env`, excluído do Git).

## Alternativas consideradas

| Opção   | Prós                                        | Contras                                                  |
|---------|---------------------------------------------|----------------------------------------------------------|
| API Key | Simples, sem estado, ideal para M2M         | Sem expiração nativa; rotação requer redeploy             |
| JWT     | Expiração, revogação granular               | Adiciona endpoint de login, gerenciamento de secrets mais complexo |

## Consequências

- **Positivas:** Implementação em < 20 linhas, sem dependência de bibliotecas extra, fácil de testar.
- **Negativas:** A API Key não expira automaticamente. Caso vaze, é necessário gerar nova chave e fazer redeploy.
- **Regras de segurança:** A variável `API_KEY` NUNCA deve ser commitada. O `.gitignore` bloqueia `.env`. Em produção, configurar via painel do Render como variável de ambiente.
