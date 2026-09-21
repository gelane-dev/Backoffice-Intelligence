"""migração inicial: usuarios, clientes, operacoes, pendencias

Revision ID: 0001_inicial
Revises:
Create Date: 2026-09-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_inicial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("email", sa.String(160), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("perfil", sa.String(20), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)

    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(160), nullable=False),
        sa.Column("documento", sa.String(20), nullable=False),
        sa.Column("email", sa.String(160), nullable=True),
        sa.Column("telefone", sa.String(30), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_clientes_nome", "clientes", ["nome"])
    op.create_index("ix_clientes_documento", "clientes", ["documento"], unique=True)

    op.create_table(
        "operacoes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(40), nullable=False),
        sa.Column("cliente_id", sa.Integer(), sa.ForeignKey("clientes.id"), nullable=True),
        sa.Column("tipo", sa.String(40), nullable=True),
        sa.Column("valor", sa.Numeric(14, 2), nullable=True),
        sa.Column("data_operacao", sa.Date(), nullable=True),
        sa.Column("data_vencimento", sa.Date(), nullable=True),
        sa.Column("status_validacao", sa.String(20), nullable=False, server_default="ok"),
        sa.Column("status_operacao", sa.String(30), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("codigo", name="uq_operacoes_codigo"),
    )
    op.create_index("ix_operacoes_codigo", "operacoes", ["codigo"])
    op.create_index("ix_operacoes_status_validacao", "operacoes", ["status_validacao"])

    op.create_table(
        "pendencias",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("operacao_id", sa.Integer(), sa.ForeignKey("operacoes.id"), nullable=False),
        sa.Column("tipo", sa.String(40), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("prazo", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pendente"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_pendencias_operacao_id", "pendencias", ["operacao_id"])
    op.create_index("ix_pendencias_status", "pendencias", ["status"])


def downgrade() -> None:
    op.drop_table("pendencias")
    op.drop_table("operacoes")
    op.drop_table("clientes")
    op.drop_table("usuarios")
