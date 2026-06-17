"""initial schema

Revision ID: 202606170001
Revises:
Create Date: 2026-06-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606170001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"])
    op.create_index(op.f("ix_users_email"), "users", ["email"])

    op.create_table(
        "broker_credentials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("broker_name", sa.String(length=50), nullable=False, server_default="definedge"),
        sa.Column("api_key", sa.Text(), nullable=False),
        sa.Column("api_secret", sa.Text(), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_broker_credentials_user_id"), "broker_credentials", ["user_id"])

    op.create_table(
        "bot_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trade_mode", sa.Enum("PAPER", "LIVE", name="trade_mode"), nullable=False),
        sa.Column("trade_type", sa.Enum("INTRADAY", "DAILY", name="trade_type"), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("timeframe", sa.String(length=50), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("RUNNING", "STOPPED", "FAILED", name="bot_status"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stopped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_bot_sessions_user_id"), "bot_sessions", ["user_id"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bot_session_id", sa.Integer(), sa.ForeignKey("bot_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("side", sa.Enum("BUY", "SELL", name="order_side"), nullable=False),
        sa.Column("order_type", sa.Enum("MARKET", "LIMIT", name="order_type"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(14, 4), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PAPER_PLACED", "PAPER_EXITED", "CANCELLED", "FAILED", name="order_status"),
            nullable=False,
        ),
        sa.Column("broker_order_id", sa.String(length=100), nullable=True),
        sa.Column("is_paper_order", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_orders_user_id"), "orders", ["user_id"])

    op.create_table(
        "positions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bot_session_id", sa.Integer(), sa.ForeignKey("bot_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("average_price", sa.Numeric(14, 4), nullable=False),
        sa.Column("ltp", sa.Numeric(14, 4), nullable=False),
        sa.Column("pnl", sa.Numeric(14, 4), nullable=False),
        sa.Column("status", sa.Enum("OPEN", "CLOSED", name="position_status"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_positions_user_id"), "positions", ["user_id"])

    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("side", sa.Enum("BUY", "SELL", name="order_side", create_type=False), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(14, 4), nullable=False),
        sa.Column("pnl", sa.Numeric(14, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f("ix_trades_user_id"), "trades", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_trades_user_id"), table_name="trades")
    op.drop_table("trades")
    op.drop_index(op.f("ix_positions_user_id"), table_name="positions")
    op.drop_table("positions")
    op.drop_index(op.f("ix_orders_user_id"), table_name="orders")
    op.drop_table("orders")
    op.drop_index(op.f("ix_bot_sessions_user_id"), table_name="bot_sessions")
    op.drop_table("bot_sessions")
    op.drop_index(op.f("ix_broker_credentials_user_id"), table_name="broker_credentials")
    op.drop_table("broker_credentials")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
