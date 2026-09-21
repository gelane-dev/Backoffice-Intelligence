from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.operacao import Operacao
from app.services.validacao import validar_operacao


def _ler_planilha(conteudo: bytes, nome: str) -> pd.DataFrame:
    buffer = BytesIO(conteudo)
    sufixo = Path(nome).suffix.lower()
    if sufixo == ".csv":
        df = pd.read_csv(buffer)
    elif sufixo in {".xlsx", ".xls"}:
        df = pd.read_excel(buffer)
    else:
        raise HTTPException(status_code=400, detail="Envie um arquivo .xlsx ou .csv")
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def _parse_data(valor):
    if pd.isna(valor) or valor == "":
        return None
    if hasattr(valor, "date"):
        return valor.date()
    parsed = pd.to_datetime(valor, errors="coerce", dayfirst=True)
    if pd.isna(parsed):
        return None
    return parsed.date()


def _obter_cliente(db: Session, documento, nome) -> Cliente | None:
    if pd.isna(documento) or not str(documento).strip():
        return None
    documento = str(documento).strip()
    cliente = db.query(Cliente).filter(Cliente.documento == documento).first()
    if cliente:
        return cliente
    nome_final = str(nome).strip() if nome and not pd.isna(nome) else f"Cliente {documento}"
    cliente = Cliente(nome=nome_final, documento=documento)
    db.add(cliente)
    db.flush()
    return cliente


def importar_arquivo(db: Session, arquivo: UploadFile) -> dict:
    conteudo = arquivo.file.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="Arquivo vazio")

    df = _ler_planilha(conteudo, arquivo.filename or "arquivo.csv")
    if "codigo" not in df.columns:
        raise HTTPException(status_code=400, detail="A planilha precisa da coluna 'codigo'")

    inseridos = 0
    atualizados = 0
    for _, linha in df.iterrows():
        codigo = str(linha.get("codigo") or "").strip()
        if not codigo or codigo.lower() == "nan":
            continue

        cliente = _obter_cliente(db, linha.get("documento_cliente"), linha.get("nome_cliente"))
        dados = {
            "codigo": codigo,
            "cliente_id": cliente.id if cliente else None,
            "tipo": None if pd.isna(linha.get("tipo")) else str(linha.get("tipo")),
            "valor": None if pd.isna(linha.get("valor")) else float(linha.get("valor")),
            "data_operacao": _parse_data(linha.get("data_operacao")),
            "data_vencimento": _parse_data(linha.get("data_vencimento")),
            "status_operacao": None
            if pd.isna(linha.get("status_operacao"))
            else str(linha.get("status_operacao")),
            "observacao": None if pd.isna(linha.get("observacao")) else str(linha.get("observacao")),
        }

        existente = db.query(Operacao).filter(Operacao.codigo == codigo).first()
        if existente:
            for campo, valor in dados.items():
                setattr(existente, campo, valor)
            validar_operacao(db, existente, ignorar_id=existente.id)
            atualizados += 1
        else:
            operacao = Operacao(**dados)
            db.add(operacao)
            db.flush()
            validar_operacao(db, operacao)
            inseridos += 1

    db.commit()
    return {
        "arquivo": arquivo.filename,
        "linhas_lidas": int(len(df)),
        "inseridos": inseridos,
        "atualizados": atualizados,
        "processado_em": datetime.utcnow().isoformat() + "Z",
    }
