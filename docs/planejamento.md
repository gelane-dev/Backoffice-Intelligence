# Planejamento — MVP Backoffice Intelligence

Duração: 14 dias corridos (~2–3 h/dia úteis, mais no fim de semana).
Escopo reduzido de propósito: entregar funcionando, não perfeito.

## Dia 0

- [x] Checagem da vaga no LinkedIn (ver nota abaixo)
- [ ] Criar repositório GitHub `backoffice-intelligence` (sem “VMB” no nome)
- [x] Estrutura `backend/`, `frontend/`, `dados_demo/`, `docs/`

**Nota sobre a vaga (20/09/2026):** o anúncio [Estágio Backoffice — corretora de seguros](https://br.linkedin.com/jobs/view/vaga-de-est%C3%A1gio-%E2%80%93-backoffice-corretora-de-seguros-at-vmb-invest-4435990223) aparece como **“Não aceita mais candidaturas”**. Ainda circulam espelhos da vaga de estágio em backoffice com foco em automação. Confirme no perfil da empresa antes de gravar o vídeo/envio.

## Semana 1 — Backend + dados

| Dia | Foco | Entregável |
|---|---|---|
| 1 | Planejamento, 4 tabelas, requirements, Docker | App sobe e conecta no banco |
| 2 | Models, Alembic, seed | ~160 registros fictícios |
| 3 | CRUD `/operacoes` | Swagger utilizável |
| 4 | `POST /importacao` + planilhas | Upload popula o banco |
| 5 | `validar_operacao()` + `/pendencias` | Classificação automática |
| 6–7 | Buffer | Corrigir, não pular etapa |

## Semana 2 — Frontend + IA + fechamento

| Dia | Foco | Entregável |
|---|---|---|
| 8 | Dashboard HTML/CSS/JS + Chart.js | Números reais |
| 9 | Central de pendências + filtro | Segunda tela |
| 10 | `POST /ia/consulta` | Caixa de pergunta |
| 11 | IA só com contexto filtrado + erros | Não quebra fora de escopo |
| 12 | JWT, 2 usuários | Login obrigatório |
| 13 | README | Texto profissional |
| 14 | Vídeo 1–2 min + mensagem | Enviar mesmo se 90% |

## 8 funcionalidades (não sair disso)

1. Login (2 perfis)
2. Importação Excel/CSV
3. Validação automática
4. Listagem de operações
5. Central de pendências
6. Dashboard + 1 gráfico
7. Assistente de IA controlado
8. README + dados fictícios + vídeo

Fora do v1: PDF/Excel export, histórico, permissões finas, gráficos avançados.

## Regra de prazo

Se um dia não render, use o buffer do fim de semana 1. Não dobre o dia seguinte. Envio no dia 14 é fixo.
