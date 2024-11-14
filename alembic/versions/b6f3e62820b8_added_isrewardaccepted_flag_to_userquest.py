"""added isRewardAccepted flag to UserQuest

Revision ID: b6f3e62820b8
Revises: d3438e0675b5
Create Date: 2024-11-03 23:29:12.650361

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6f3e62820b8'
down_revision: Union[str, None] = 'd3438e0675b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_quest_progress', sa.Column('is_reward_accepted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_quest_progress', 'is_reward_accepted')
    # ### end Alembic commands ###