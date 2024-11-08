"""added long_description to Quest model

Revision ID: d3438e0675b5
Revises: 40f521d4eea8
Create Date: 2024-10-28 18:45:34.454413

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3438e0675b5'
down_revision: Union[str, None] = '40f521d4eea8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('quests', sa.Column('long_description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('quests', 'long_description')
    # ### end Alembic commands ###
