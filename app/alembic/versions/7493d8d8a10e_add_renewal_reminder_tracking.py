"""add renewal reminder tracking

Revision ID: 7493d8d8a10e
Revises: 2b80db066b3d
Create Date: 2026-08-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7493d8d8a10e"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "2b80db066b3d"

branch_labels: Union[
    str,
    Sequence[str],
    None
] = None

depends_on: Union[
    str,
    Sequence[str],
    None
] = None


def upgrade() -> None:

    op.add_column(
        "subscriptions",
        sa.Column(
            "renewal_reminder_sent",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )


def downgrade() -> None:

    op.drop_column(
        "subscriptions",
        "renewal_reminder_sent"
    )