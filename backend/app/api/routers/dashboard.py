from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_usuario_atual
from app.models.operacao import Operacao
from app.models.usuario import Usuario
from app.schemas import DashboardOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def indicadores(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_usuario_atual),
):
    total = db.query(func.count(Operacao.id)).scalar() or 0
    agrupado = dict(
        db.query(Operacao.status_validacao, func.count(Operacao.id))
        .group_by(Operacao.status_validacao)
        .all()
    )
    return DashboardOut(
        total=total,
        ok=int(agrupado.get("ok", 0)),
        pendencias=int(agrupado.get("pendencia", 0)),
        inconsistencias=int(agrupado.get("inconsistencia", 0)),
        por_status={
            "ok": int(agrupado.get("ok", 0)),
            "pendencia": int(agrupado.get("pendencia", 0)),
            "inconsistencia": int(agrupado.get("inconsistencia", 0)),
        },
    )
