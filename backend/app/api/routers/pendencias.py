from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_usuario_atual
from app.models.operacao import Operacao
from app.models.pendencia import Pendencia
from app.models.usuario import Usuario
from app.schemas import PendenciaOut, PendenciaUpdate

router = APIRouter(prefix="/pendencias", tags=["pendencias"])


@router.get("", response_model=list[PendenciaOut])
def listar(
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    consulta = db.query(Pendencia).join(Operacao, Pendencia.operacao_id == Operacao.id)
    if status:
        consulta = consulta.filter(Pendencia.status == status)
    itens = consulta.order_by(Pendencia.id.desc()).all()
    return [
        PendenciaOut(
            id=item.id,
            operacao_id=item.operacao_id,
            tipo=item.tipo,
            descricao=item.descricao,
            prazo=item.prazo,
            status=item.status,
            codigo_operacao=item.operacao.codigo if item.operacao else None,
        )
        for item in itens
    ]


@router.patch("/{pendencia_id}", response_model=PendenciaOut)
def atualizar_pendencia(
    pendencia_id: int,
    payload: PendenciaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    pendencia = db.get(Pendencia, pendencia_id)
    if not pendencia:
        raise HTTPException(status_code=404, detail="Pendência não encontrada")

    if payload.status is not None:
        pendencia.status = payload.status
    if payload.prazo is not None:
        pendencia.prazo = payload.prazo
    if payload.descricao is not None:
        pendencia.descricao = payload.descricao

    db.flush()

    # Reavalia o status da operação associada
    operacao = pendencia.operacao
    if operacao:
        pendencias_abertas = [
            p for p in operacao.pendencias if p.status != "resolvido"
        ]
        if not pendencias_abertas:
            operacao.status_validacao = "ok"
        elif any(p.status == "critico" for p in pendencias_abertas):
            operacao.status_validacao = "inconsistencia"
        else:
            operacao.status_validacao = "pendencia"

    db.commit()
    db.refresh(pendencia)
    return PendenciaOut(
        id=pendencia.id,
        operacao_id=pendencia.operacao_id,
        tipo=pendencia.tipo,
        descricao=pendencia.descricao,
        prazo=pendencia.prazo,
        status=pendencia.status,
        codigo_operacao=operacao.codigo if operacao else None,
    )


@router.delete("/{pendencia_id}", status_code=204)
def excluir_pendencia(
    pendencia_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    pendencia = db.get(Pendencia, pendencia_id)
    if not pendencia:
        raise HTTPException(status_code=404, detail="Pendência não encontrada")

    operacao = pendencia.operacao
    db.delete(pendencia)
    db.flush()

    if operacao:
        pendencias_abertas = [
            p for p in operacao.pendencias if p.status != "resolvido" and p.id != pendencia_id
        ]
        if not pendencias_abertas:
            operacao.status_validacao = "ok"
        elif any(p.status == "critico" for p in pendencias_abertas):
            operacao.status_validacao = "inconsistencia"
        else:
            operacao.status_validacao = "pendencia"

    db.commit()
    return None

