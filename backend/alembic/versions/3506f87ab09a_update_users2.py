"""update  users2

Revision ID: 3506f87ab09a
Revises: 35db378157db
Create Date: 2026-04-13 ...

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3506f87ab09a"
down_revision: Union[str, Sequence[str], None] = "35db378157db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass