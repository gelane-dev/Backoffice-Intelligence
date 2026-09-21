from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_usuario_atual
from app.models.usuario import Usuario
from app.services.importacao import importar_arquivo

router = APIRouter(prefix="/importacao", tags=["importacao"])


@router.post("")
def importar(
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    return importar_arquivo(db, arquivo)
