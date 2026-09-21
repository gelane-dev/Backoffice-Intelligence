from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import criar_token, get_usuario_atual, verificar_senha
from app.models.usuario import Usuario
from app.schemas import LoginIn, TokenOut, UsuarioOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _autenticar(db: Session, email: str, senha: str) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    if not usuario.ativo:
        raise HTTPException(status_code=401, detail="Usuário inativo")
    return usuario


@router.post("/login", response_model=TokenOut)
def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = _autenticar(db, form.username, form.password)
    return TokenOut(access_token=criar_token(usuario), nome=usuario.nome, perfil=usuario.perfil)


@router.post("/login-json", response_model=TokenOut)
def login_json(payload: LoginIn, db: Session = Depends(get_db)):
    usuario = _autenticar(db, payload.email, payload.senha)
    return TokenOut(access_token=criar_token(usuario), nome=usuario.nome, perfil=usuario.perfil)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_usuario_atual)):
    return usuario
