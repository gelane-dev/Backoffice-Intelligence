# Backoffice Intelligence

MVP independente de consolidação, validação e consulta inteligente de operações de backoffice.

**Aviso:** todos os dados são fictícios. Este repositório não é produto oficial de nenhuma instituição. Foi inspirado em rotinas reais de backoffice financeiro (planilhas, pendências, conferência de datas e duplicidade).

## Problema

Operações chegam em Excel/CSV, ficam espalhadas e só são conferidas no olho. Campo vazio, data invertida e código duplicado geram retrabalho e atraso.

## Solução

1. Login com dois perfis (admin e operador).
2. Importação de `.xlsx` / `.csv`.
3. Validação automática (vazio, duplicidade, data).
4. Listagem de operações.
5. Central de pendências com filtro.
6. Dashboard com indicadores e um gráfico.
7. Assistente de IA com consulta **controlada** (o modelo só vê um recorte já filtrado, nunca o banco inteiro).
8. Dados demo + este README.

## Arquitetura

```
planilha → API FastAPI → PostgreSQL
                 ↓
         validar_operacao()
                 ↓
     dashboard / pendências / IA
```

Camadas no backend:

- `app/api` — rotas HTTP
- `app/services` — regras (validação, importação, assistente)
- `app/models` — tabelas SQLAlchemy
- `app/schemas` — contratos Pydantic
- `app/core` — config, banco, JWT

Banco (4 tabelas): `usuarios`, `clientes`, `operacoes`, `pendencias`.

Detalhes em `docs/arquitetura.md`.

## Como rodar

Pré-requisitos: Docker, Python 3.11+.

```bash
docker compose up -d
copy .env.example .env   # Windows
# cp .env.example .env  # macOS/Linux

cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

Abra:

- App: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Saúde do banco: http://localhost:8000/health

Logins demo:

- `admin@backoffice.local` / `admin123`
- `operador@backoffice.local` / `operador123`

Planilhas de teste em `dados_demo/` (geradas no seed).

IA: sem `LLM_API_KEY` o assistente responde com o recorte local. Com chave OpenAI-compatible, usa o modelo configurado no `.env`.

## Fora do MVP v1

- Relatórios PDF/Excel
- Histórico completo de alterações
- Permissões granulares
- Gráficos avançados

## Documentação

- `docs/planejamento.md` — cronograma de 14 dias
- `docs/arquitetura.md` — desenho técnico
- `docs/mensagem-gestor.md` — rascunho do envio (Dia 14)
