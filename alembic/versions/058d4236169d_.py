"""empty message

Revision ID: 058d4236169d
Revises: 9c820fb56324
Create Date: 2024-10-10 16:04:22.420227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '058d4236169d'
down_revision: Union[str, None] = '9c820fb56324'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
