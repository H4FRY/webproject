"""update users3

Revision ID: f3306b1743b6
Revises: 3506f87ab09a
Create Date: 2026-04-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3306b1743b6"
down_revision: Union[str, Sequence[str], None] = "3506f87ab09a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass