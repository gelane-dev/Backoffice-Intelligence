from datetime import date

import httpx
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.operacao import Operacao
from app.models.pendencia import Pendencia

FORA_DE_ESCOPO = (
    "Consigo ajudar só com operações, pendências, prazos e indicadores deste backoffice. "
    "Pergunte, por exemplo: operações atrasadas, resumo de pendências ou inconsistências."
)


def pergunta_no_escopo(pergunta: str) -> bool:
    termos = [
        "opera",
        "penden",
        "atras",
        "inconsist",
        "valid",
        "cliente",
        "dashboard",
        "indicador",
        "resumo",
        "status",
        "venc",
        "import",
        "valor",
        "prazo",
        "critico",
        "ok",
    ]
    texto = pergunta.lower()
    return any(t in texto for t in termos)


def montar_contexto(db: Session) -> tuple[str, int]:
    hoje = date.today()
    operacoes = (
        db.query(Operacao)
        .options(joinedload(Operacao.cliente), joinedload(Operacao.pendencias))
        .all()
    )
    atrasadas = [
        op
        for op in operacoes
        if op.data_vencimento and op.data_vencimento < hoje
    ]
    pendencias = db.query(Pendencia).all()

    linhas = [
        f"Total de operações: {len(operacoes)}",
        f"OK: {sum(1 for o in operacoes if o.status_validacao == 'ok')}",
        f"Pendência: {sum(1 for o in operacoes if o.status_validacao == 'pendencia')}",
        f"Inconsistência: {sum(1 for o in operacoes if o.status_validacao == 'inconsistencia')}",
        f"Pendências abertas: {sum(1 for p in pendencias if p.status != 'resolvido')}",
        f"Pendências críticas: {sum(1 for p in pendencias if p.status == 'critico')}",
        f"Operações com vencimento atrasado: {len(atrasadas)}",
        "Amostra de operações atrasadas:",
    ]
    for op in atrasadas[:15]:
        cliente = op.cliente.nome if op.cliente else "sem cliente"
        linhas.append(
            f"- {op.codigo} | {cliente} | venc. {op.data_vencimento} | validação={op.status_validacao}"
        )
    linhas.append("Amostra de pendências:")
    for p in pendencias[:20]:
        codigo = p.operacao.codigo if p.operacao else "?"
        linhas.append(f"- {codigo} | {p.tipo} | {p.status} | prazo {p.prazo} | {p.descricao}")
    return "\n".join(linhas), len(operacoes)


def resposta_local(pergunta: str, contexto: str) -> str:
    texto = pergunta.lower()
    if "atras" in texto:
        return "Com base nos dados filtrados:\n" + "\n".join(contexto.splitlines()[6:24])
    if "penden" in texto:
        linhas = [l for l in contexto.splitlines() if "Pendên" in l or "prazo" in l]
        return "Resumo de pendências:\n" + "\n".join(linhas[:25])
    return "Indicadores atuais do backoffice:\n" + "\n".join(contexto.splitlines()[:8])


async def chamar_llm(pergunta: str, contexto: str) -> str | None:
    if not settings.llm_api_key:
        return None
    payload = {
        "model": settings.llm_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é um assistente de backoffice financeiro. "
                    "Responda em português, de forma objetiva, somente com o contexto fornecido. "
                    "Não invente números. Se o contexto não cobrir a pergunta, diga que não há dados."
                ),
            },
            {
                "role": "user",
                "content": f"CONTEXTO FILTRADO:\n{contexto}\n\nPERGUNTA:\n{pergunta}",
            },
        ],
        "temperature": 0.1,
    }
    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
    async with httpx.AsyncClient(timeout=30) as client:
        resposta = await client.post(url, json=payload, headers=headers)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados["choices"][0]["message"]["content"]
