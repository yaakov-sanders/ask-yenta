"""add yenta_block_id column

Revision ID: add_yenta_block_id
Revises: 058c7e3072f6
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_yenta_block_id'
down_revision: Union[str, None] = '058c7e3072f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add yenta_block_id column to user table
    op.add_column('user', sa.Column('yenta_block_id', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove yenta_block_id column from user table
    op.drop_column('user', 'yenta_block_id') 