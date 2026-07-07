---
name: ADR-0004
description: Render como plataforma de deploy da API
alwaysApply: false
---

# ADR-0004: Render como plataforma de deploy da API

**Data:** 2026-07-06
**Status:** Aceito
**Autores:** Equipe do projeto

## Contexto

A spec (seção 5 do projeto_final.md) exige que a API seja publicada em provedor de nuvem
com URL pública. As opções listadas são: Render, Hugging Face Spaces, Railway ou Fly.io.

## Decisão

Utilizamos o **Render** como plataforma de deploy, com um arquivo `render.yaml` declarativo
na raiz do repositório para configurar o Web Service automaticamente via Connect de repositório GitHub.

## Alternativas consideradas

| Plataforma         | Prós                                               | Contras                                           |
|--------------------|-----------------------------------------------------|---------------------------------------------------|
| **Render**         | Free tier, deploy automático via Git, `render.yaml` | Sleep em inatividade no free tier                 |
| Hugging Face Spaces| Ótimo para ML demos, comunidade grande              | Requer Dockerfile, menos padrão para APIs REST   |
| Railway            | Interface moderna, fácil                            | Free tier mais limitado atualmente               |
| Fly.io             | Bom desempenho global                               | Requer CLI e fly.toml, curva maior               |

## Consequências

- **Positivas:** Deploy automático em cada push na branch main; configuração declarativa via `render.yaml`; zero custo no free tier.
- **Negativas:** Instâncias no free tier "adormecem" após 15 minutos de inatividade — o primeiro request após inatividade pode demorar ~30s (cold start).
- **Mitigação:** Documentar o cold start no README para o avaliador não confundir com lentidão do solver.
- **Variáveis de ambiente:** `API_KEY` deve ser configurada no painel do Render (Settings → Environment), nunca via arquivo commitado.
