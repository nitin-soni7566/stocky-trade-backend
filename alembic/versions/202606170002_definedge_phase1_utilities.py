"""definedge phase1 utilities

Revision ID: 202606170002
Revises: 202606170001
Create Date: 2026-06-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606170002"
down_revision: str | None = "202606170001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("bot_sessions", sa.Column("exchange", sa.String(length=20), nullable=True))
    op.add_column("bot_sessions", sa.Column("token", sa.String(length=50), nullable=True))

    op.create_table(
        "broker_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("broker_name", sa.String(length=50), nullable=False),
        sa.Column("api_session_key", sa.Text(), nullable=False),
        sa.Column("susertoken", sa.Text(), nullable=True),
        sa.Column("uid", sa.String(length=100), nullable=True),
        sa.Column("actid", sa.String(length=100), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_broker_sessions_user_id"), "broker_sessions", ["user_id"])

    op.create_table(
        "instruments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange", sa.String(length=20), nullable=False),
        sa.Column("token", sa.String(length=50), nullable=False),
        sa.Column("symbol", sa.String(length=100), nullable=True),
        sa.Column("tradingsymbol", sa.String(length=150), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("instrument_type", sa.String(length=50), nullable=True),
        sa.Column("lot_size", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("exchange", "token", name="uq_instruments_exchange_token"),
    )
    op.create_index(op.f("ix_instruments_exchange"), "instruments", ["exchange"])
    op.create_index(op.f("ix_instruments_token"), "instruments", ["token"])
    op.create_index(op.f("ix_instruments_symbol"), "instruments", ["symbol"])
    op.create_index(op.f("ix_instruments_tradingsymbol"), "instruments", ["tradingsymbol"])


def downgrade() -> None:
    op.drop_index(op.f("ix_instruments_tradingsymbol"), table_name="instruments")
    op.drop_index(op.f("ix_instruments_symbol"), table_name="instruments")
    op.drop_index(op.f("ix_instruments_token"), table_name="instruments")
    op.drop_index(op.f("ix_instruments_exchange"), table_name="instruments")
    op.drop_table("instruments")
    op.drop_index(op.f("ix_broker_sessions_user_id"), table_name="broker_sessions")
    op.drop_table("broker_sessions")
    op.drop_column("bot_sessions", "token")
    op.drop_column("bot_sessions", "exchange")
