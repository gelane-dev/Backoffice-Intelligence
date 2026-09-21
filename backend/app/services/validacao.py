from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.operacao import Operacao
from app.models.pendencia import Pendencia

CAMPOS_OBRIGATORIOS = {
    "codigo": "Código da operação",
    "tipo": "Tipo da operação",
    "valor": "Valor",
    "data_operacao": "Data da operação",
    "data_vencimento": "Data de vencimento",
}


def validar_operacao(db: Session, operacao: Operacao, ignorar_id: Optional[int] = None) -> str:
    """Classifica a operação como ok / pendencia / inconsistencia e gera pendências."""
    for item in list(operacao.pendencias):
        db.delete(item)
    db.flush()

    problemas: list[tuple[str, str, str, int]] = []

    for campo, rotulo in CAMPOS_OBRIGATORIOS.items():
        valor = getattr(operacao, campo)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            problemas.append(("campo_vazio", f"{rotulo} está vazio", "pendente", 5))

    if operacao.data_operacao and operacao.data_vencimento:
        if operacao.data_vencimento < operacao.data_operacao:
            problemas.append(
                ("data_invalida", "Data de vencimento anterior à data da operação", "critico", 1)
            )

    if operacao.codigo:
        consulta = db.query(Operacao).filter(Operacao.codigo == operacao.codigo)
        alvo = ignorar_id if ignorar_id is not None else operacao.id
        if alvo:
            consulta = consulta.filter(Operacao.id != alvo)
        if consulta.first():
            problemas.append(("duplicidade", f"Código {operacao.codigo} já existe", "critico", 1))

    if operacao.data_vencimento and operacao.data_vencimento < date.today():
        problemas.append(("atraso", "Operação com vencimento atrasado", "critico", 0))

    tipos = {p[0] for p in problemas}
    if "duplicidade" in tipos or "data_invalida" in tipos:
        status = "inconsistencia"
    elif problemas:
        status = "pendencia"
    else:
        status = "ok"

    operacao.status_validacao = status
    for tipo, descricao, status_pend, dias in problemas:
        db.add(
            Pendencia(
                operacao=operacao,
                tipo=tipo,
                descricao=descricao,
                prazo=date.today() + timedelta(days=dias),
                status=status_pend,
            )
        )
    return status
