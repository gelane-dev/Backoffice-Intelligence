# Arquitetura — Backoffice Intelligence

Projeto independente, dados fictícios, inspirado em backoffice financeiro.

## Visão

O sistema recebe planilhas, persiste operações, classifica qualidade dos dados e expõe três superfícies: dashboard, central de pendências e um assistente que só consulta um **contexto já filtrado**.

```
┌─────────────┐     ┌──────────────────┐     ┌────────────┐
│  Frontend   │────▶│  FastAPI (API)   │────▶│ PostgreSQL │
│ HTML/CSS/JS │     │  routers + JWT   │     │  4 tabelas │
└─────────────┘     └────────┬─────────┘     └────────────┘
                             │
                    ┌────────▼─────────┐
                    │    Services      │
                    │ validação        │
                    │ importação       │
                    │ assistente (LLM) │
                    └──────────────────┘
```

## Camadas

| Pasta | Responsabilidade |
|---|---|
| `frontend/` | Telas (login, dashboard, pendências, IA) |
| `backend/app/api/routers` | HTTP, autenticação nas rotas |
| `backend/app/services` | Regras de negócio |
| `backend/app/models` | Mapeamento das 4 tabelas |
| `backend/app/schemas` | Contratos de entrada/saída |
| `backend/app/core` | Config, engine, JWT |
| `dados_demo/` | Planilhas fictícias |
| `docs/` | Planejamento e este desenho |

## Modelo de dados

- **usuarios**: email, senha hash, perfil `admin` ou `operador`
- **clientes**: nome, documento
- **operacoes**: código único, tipo, valor, datas, `status_validacao` (`ok` / `pendencia` / `inconsistencia`)
- **pendencias**: tipo (`campo_vazio`, `data_invalida`, `duplicidade`, `atraso`), prazo, status (`critico` / `pendente` / `resolvido`)

## Motor de validação

`validar_operacao()` é o centro do MVP:

1. Campo obrigatório vazio → pendência
2. Vencimento anterior à data da operação → inconsistência crítica
3. Código duplicado → inconsistência crítica
4. Vencimento no passado → pendência crítica de atraso

Cada importação ou CRUD dispara essa função de novo.

## Assistente de IA (consulta controlada)

Fluxo fixo:

1. Usuário autentica e envia texto em `POST /ia/consulta`
2. O sistema rejeita pergunta fora de escopo
3. O sistema monta um resumo (totais, amostra de atrasos, amostra de pendências)
4. Só esse texto + a pergunta vão para a API de LLM
5. Se a LLM falhar ou não houver chave, responde com o mesmo resumo local

A LLM **não** recebe SQL, connection string nem acesso irrestrito ao banco.

## Segurança do MVP

- JWT nas rotas de dados
- Senhas com hash bcrypt
- Segredo e chave de LLM no `.env` (não versionar)

Não é produção: CORS aberto, dois usuários fixos, sem rate limit.
