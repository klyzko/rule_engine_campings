"""Initial migration

Revision ID: ea3cf3243137
Revises: dbe3e1ad90a4
Create Date: 2026-06-19 01:43:40.201472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea3cf3243137'
down_revision: Union[str, Sequence[str], None] = 'dbe3e1ad90a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
