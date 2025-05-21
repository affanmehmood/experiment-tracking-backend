"""add ResourceUsage table

Revision ID: 18bc5a720536
Revises: 205137e30c24
Create Date: 2025-05-21 17:44:07.902850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '18bc5a720536'
down_revision: Union[str, None] = '205137e30c24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'resource_usage',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('experiment_id', sa.Integer(), sa.ForeignKey('experiments.id')),
        sa.Column('epoch', sa.Integer(), index=True),
        sa.Column('cpu_usage_percent', sa.Float()),
        sa.Column('memory_usage_mb', sa.Float()),
        sa.Column('gpu_usage_percent', sa.Float()),
        sa.Column('gpu_memory_usage_mb', sa.Float()),
        sa.Column('training_time_sec', sa.Float()),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now())
    )


def downgrade():
    op.drop_table('resource_usage')