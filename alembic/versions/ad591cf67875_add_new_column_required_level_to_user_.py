"""Add new column required_level to User model

Revision ID: ad591cf67875
Revises: c39726bc1c61
Create Date: 2024-10-27 09:50:38.293875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad591cf67875'
down_revision: Union[str, None] = 'c39726bc1c61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('quests', sa.Column('requiredLevel', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('quests', 'requiredLevel')
    # ### end Alembic commands ###
