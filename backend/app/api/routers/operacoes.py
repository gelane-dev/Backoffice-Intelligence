from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_usuario_atual
from app.models.operacao import Operacao
from app.models.usuario import Usuario
from app.schemas import OperacaoCreate, OperacaoOut, OperacaoUpdate
from app.services.validacao import validar_operacao

router = APIRouter(prefix="/operacoes", tags=["operacoes"])


@router.get("", response_model=list[OperacaoOut])
def listar(
    status_validacao: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    consulta = db.query(Operacao).options(joinedload(Operacao.cliente))
    if status_validacao:
        consulta = consulta.filter(Operacao.status_validacao == status_validacao)
    return consulta.order_by(Operacao.id.desc()).all()


@router.get("/{operacao_id}", response_model=OperacaoOut)
def obter(
    operacao_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    operacao = (
        db.query(Operacao)
        .options(joinedload(Operacao.cliente))
        .filter(Operacao.id == operacao_id)
        .first()
    )
    if not operacao:
        raise HTTPException(status_code=404, detail="Operação não encontrada")
    return operacao


@router.post("", response_model=OperacaoOut, status_code=201)
def criar(
    payload: OperacaoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    operacao = Operacao(**payload.model_dump())
    db.add(operacao)
    db.flush()
    validar_operacao(db, operacao)
    db.commit()
    db.refresh(operacao)
    return operacao


@router.put("/{operacao_id}", response_model=OperacaoOut)
def atualizar(
    operacao_id: int,
    payload: OperacaoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    operacao = db.get(Operacao, operacao_id)
    if not operacao:
        raise HTTPException(status_code=404, detail="Operação não encontrada")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(operacao, campo, valor)
    validar_operacao(db, operacao, ignorar_id=operacao.id)
    db.commit()
    db.refresh(operacao)
    return operacao


@router.delete("/todas/limpar", status_code=200)
def limpar_todas(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    total = db.query(Operacao).count()
    from app.models.pendencia import Pendencia
    db.query(Pendencia).delete()
    db.query(Operacao).delete()
    db.commit()
    return {"mensagem": f"{total} operações removidas com sucesso"}


@router.delete("/{operacao_id}", status_code=204)
def excluir(
    operacao_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    operacao = db.get(Operacao, operacao_id)
    if not operacao:
        raise HTTPException(status_code=404, detail="Operação não encontrada")
    db.delete(operacao)
    db.commit()
    return None

