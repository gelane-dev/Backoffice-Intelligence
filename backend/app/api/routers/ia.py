from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_usuario_atual
from app.models.usuario import Usuario
from app.schemas import ConsultaIAIn, ConsultaIAOut
from app.services.assistente import (
    FORA_DE_ESCOPO,
    chamar_llm,
    montar_contexto,
    pergunta_no_escopo,
    resposta_local,
)

router = APIRouter(prefix="/ia", tags=["ia"])


@router.post("/consulta", response_model=ConsultaIAOut)
async def consultar(
    payload: ConsultaIAIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    pergunta = payload.pergunta.strip()
    if not pergunta_no_escopo(pergunta):
        return ConsultaIAOut(
            pergunta=pergunta,
            resposta=FORA_DE_ESCOPO,
            usado_llm=False,
            registros_considerados=0,
        )

    contexto, total = montar_contexto(db)
    if total == 0:
        return ConsultaIAOut(
            pergunta=pergunta,
            resposta="Não há operações cadastradas para analisar. Importe uma planilha primeiro.",
            usado_llm=False,
            registros_considerados=0,
        )

    usado_llm = False
    try:
        resposta = await chamar_llm(pergunta, contexto)
        if resposta:
            usado_llm = True
        else:
            resposta = resposta_local(pergunta, contexto)
    except Exception as exc:
        print(f"[ERRO LLM]: {exc}")
        resposta = resposta_local(pergunta, contexto) + (
            "\n\n(A API de LLM não respondeu; usei o resumo local dos dados já filtrados.)"
        )

    return ConsultaIAOut(
        pergunta=pergunta,
        resposta=resposta,
        usado_llm=usado_llm,
        registros_considerados=total,
    )
