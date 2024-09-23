"""remove test column

Revision ID: d88fa3e10308
Revises: 64809431b0a8
Create Date: 2024-09-23 23:40:38.301358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd88fa3e10308'
down_revision: Union[str, None] = '64809431b0a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'testColumn')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('testColumn', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
