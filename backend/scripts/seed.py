"""Popula o banco com usuários, clientes, operações e planilhas demo."""

from __future__ import annotations

import random
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_senha  # noqa: E402
from app.models.cliente import Cliente  # noqa: E402
from app.models.operacao import Operacao  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402
from app.services.validacao import validar_operacao  # noqa: E402

TIPOS = ["seguro", "consorcio", "financiamento", "plano_saude", "investimento"]
NOMES = [
    "Ana Souza",
    "Bruno Lima",
    "Carla Mendes",
    "Diego Alves",
    "Elena Castro",
    "Felipe Rocha",
    "Gabriela Nunes",
    "Henrique Dias",
    "Isabela Pinto",
    "João Martins",
    "Karina Lopes",
    "Lucas Ferreira",
    "Marina Costa",
    "Nicolas Barbosa",
    "Olivia Teixeira",
    "Paulo Henrique",
    "Queila Ramos",
    "Rafael Vieira",
    "Sofia Cardoso",
    "Thiago Moreira",
]


def _clientes(db: Session) -> list[Cliente]:
    existentes = db.query(Cliente).all()
    if existentes:
        return existentes
    criados = []
    for i, nome in enumerate(NOMES, start=1):
        cliente = Cliente(
            nome=nome,
            documento=f"{10000000000 + i:011d}",
            email=f"{nome.split()[0].lower()}@demo.local",
            telefone=f"(21) 9{1000 + i:04d}-{2000 + i:04d}",
        )
        db.add(cliente)
        criados.append(cliente)
    db.flush()
    return criados


def _usuarios(db: Session) -> None:
    if db.query(Usuario).first():
        return
    db.add_all(
        [
            Usuario(
                nome="Administrador",
                email="admin@backoffice.local",
                senha_hash=hash_senha("admin123"),
                perfil="admin",
            ),
            Usuario(
                nome="Operador",
                email="operador@backoffice.local",
                senha_hash=hash_senha("operador123"),
                perfil="operador",
            ),
        ]
    )


def _operacoes(db: Session, clientes: list[Cliente]) -> list[dict]:
    if db.query(Operacao).count() >= 120:
        return []

    random.seed(42)
    hoje = date.today()
    linhas_planilha = []

    for i in range(1, 161):
        codigo = f"OP-{i:04d}"
        if db.query(Operacao).filter(Operacao.codigo == codigo).first():
            continue

        cliente = random.choice(clientes)
        tipo = random.choice(TIPOS)
        valor = round(random.uniform(1500, 85000), 2)
        data_op = hoje - timedelta(days=random.randint(5, 120))
        data_venc = data_op + timedelta(days=random.randint(10, 90))
        observacao = None
        if i % 17 == 0:
            valor = None
            observacao = "Valor ausente na origem"
        if i % 19 == 0:
            data_venc = data_op - timedelta(days=3)
            observacao = "Data invertida"
        if i % 23 == 0:
            data_venc = hoje - timedelta(days=random.randint(1, 20))
        if i % 29 == 0:
            tipo = None

        operacao = Operacao(
            codigo=codigo,
            cliente_id=cliente.id,
            tipo=tipo,
            valor=valor,
            data_operacao=data_op,
            data_vencimento=data_venc,
            status_operacao="aberta",
            observacao=observacao,
        )
        db.add(operacao)
        db.flush()
        validar_operacao(db, operacao)
        linhas_planilha.append(
            {
                "codigo": codigo,
                "documento_cliente": cliente.documento,
                "nome_cliente": cliente.nome,
                "tipo": tipo or "",
                "valor": valor if valor is not None else "",
                "data_operacao": data_op.isoformat(),
                "data_vencimento": data_venc.isoformat() if data_venc else "",
                "status_operacao": "aberta",
                "observacao": observacao or "",
            }
        )
    return linhas_planilha


def _planilhas(linhas: list[dict]) -> None:
    destino = ROOT.parent / "dados_demo"
    destino.mkdir(exist_ok=True)
    df = pd.DataFrame(linhas)
    if df.empty:
        return
    df.to_csv(destino / "operacoes_demo.csv", index=False)
    df.to_excel(destino / "operacoes_demo.xlsx", index=False)
    df.head(25).to_excel(destino / "operacoes_amostra.xlsx", index=False)


def main() -> None:
    db = SessionLocal()
    try:
        _usuarios(db)
        clientes = _clientes(db)
        linhas = _operacoes(db, clientes)
        db.commit()
        _planilhas(linhas)
        print("Seed concluído.")
        print("  admin@backoffice.local / admin123")
        print("  operador@backoffice.local / operador123")
    finally:
        db.close()


if __name__ == "__main__":
    main()
