from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_usuario_atual
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.schemas import ClienteOut

router = APIRouter(prefix="/clientes", tags=["clientes"])


class ClienteCreate(BaseModel):
    nome: str
    documento: str
    email: Optional[str] = None
    telefone: Optional[str] = None


@router.get("", response_model=list[ClienteOut])
def listar_clientes(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    return db.query(Cliente).order_by(Cliente.nome.asc()).all()


@router.post("", response_model=ClienteOut, status_code=201)
def criar_cliente(
    payload: ClienteCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    cliente = Cliente(**payload.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente
