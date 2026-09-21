from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.routers import auth, clientes, dashboard, ia, importacao, operacoes, pendencias
from app.core.database import engine
from app import models  # noqa: F401 — registra metadata

app = FastAPI(
    title="Backoffice Intelligence",
    description=(
        "MVP de consolidação, validação e consulta inteligente de operações de backoffice. "
        "Todos os dados são fictícios. Projeto independente, inspirado em rotinas de backoffice financeiro."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(operacoes.router)
app.include_router(importacao.router)
app.include_router(pendencias.router)
app.include_router(dashboard.router)
app.include_router(ia.router)


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")
