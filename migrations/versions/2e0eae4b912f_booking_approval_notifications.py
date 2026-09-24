"""add booking approval state and notification session links

Revision ID: 2e0eae4b912f
Revises: c286e8854ae2
Create Date: 2026-07-30 12:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "2e0eae4b912f"
down_revision = "c286e8854ae2"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    is_mysql = bind.dialect.name == "mysql"

    # MySQL stores ENUM types; this DDL expands the allowed values.
    # SQLite stores them as TEXT and doesn't need a MODIFY COLUMN.
    if is_mysql:
        op.execute(
            "ALTER TABLE sessions MODIFY COLUMN status "
            "ENUM('pending', 'confirmed', 'completed', 'cancelled', 'no_show') NOT NULL"
        )

    # The initial schema (c286e8854ae2) already creates notifications.session_id on
    # some DB engines. Only add the column when it doesn't yet exist.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_cols = [c["name"] for c in inspector.get_columns("notifications")]
    if "session_id" not in existing_cols:
        op.add_column("notifications", sa.Column("session_id", sa.Integer(), nullable=True))
        op.create_index("ix_notifications_session_id", "notifications", ["session_id"])

    # SQLite doesn't support standalone ADD CONSTRAINT — skip it; the FK is
    # enforced at the ORM level and the index is enough for queries.
    if is_mysql:
        op.create_foreign_key(
            "fk_notifications_session_id", "notifications", "sessions", ["session_id"], ["id"]
        )


def downgrade():
    op.execute("UPDATE sessions SET status = 'cancelled' WHERE status = 'pending'")

    bind = op.get_bind()
    is_mysql = bind.dialect.name == "mysql"

    if is_mysql:
        op.drop_constraint("fk_notifications_session_id", "notifications", type_="foreignkey")

    op.drop_index("ix_notifications_session_id", table_name="notifications")
    op.drop_column("notifications", "session_id")

    if is_mysql:
        op.execute(
            "ALTER TABLE sessions MODIFY COLUMN status "
            "ENUM('confirmed', 'completed', 'cancelled', 'no_show') NOT NULL"
        )
