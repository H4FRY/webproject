"""update  users

Revision ID: 35db378157db
Revises: 45ce15433eee
Create Date: 2026-04-13 18:03:59.553728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35db378157db'
down_revision: Union[str, Sequence[str], None] = '45ce15433eee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass