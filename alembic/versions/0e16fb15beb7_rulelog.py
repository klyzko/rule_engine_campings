"""ruleюlog

Revision ID: 0e16fb15beb7
Revises: dfb37bbffce6
Create Date: 2026-06-21 20:42:16.490430

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0e16fb15beb7'
down_revision: Union[str, Sequence[str], None] = 'dfb37bbffce6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем объект ENUM с указанием, что не нужно создавать тип заново
    campaign_status = postgresql.ENUM('ACTIVE', 'PAUSED', name='campaignstatus', create_type=False)

    op.create_table('rule_evaluation_log',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('campaign_id', sa.UUID(), nullable=False),
    sa.Column('triggered_rule', sa.String(), nullable=True, comment='Какое правило сработало (null = нет ограничений)'),
    sa.Column('previous_target', campaign_status, nullable=True),
    sa.Column('new_target', campaign_status, nullable=True),
    sa.Column('context', sa.JSON(), nullable=False, comment='Снапшот данных на момент вычисления'),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rule_evaluation_log_campaign_id'), 'rule_evaluation_log', ['campaign_id'], unique=False)

    op.drop_index('ix_campaign_status_history_campaign_id', table_name='campaign_status_history')
    op.drop_table('campaign_status_history')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table('campaign_status_history',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('campaign_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('triggered_rule', sa.VARCHAR(), autoincrement=False, nullable=True, comment='Название правила, которое вызвало изменение (null = ручное изменение)'),
    sa.Column('previous_target', postgresql.ENUM('ACTIVE', 'PAUSED', name='campaignstatus'), autoincrement=False, nullable=True),
    sa.Column('new_target', postgresql.ENUM('ACTIVE', 'PAUSED', name='campaignstatus'), autoincrement=False, nullable=True),
    sa.Column('context', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False, comment='Снапшот данных на момент вычисления: расход, остатки и т.д.'),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], name='campaign_status_history_campaign_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='campaign_status_history_pkey')
    )
    op.create_index('ix_campaign_status_history_campaign_id', 'campaign_status_history', ['campaign_id'], unique=False)
    op.drop_index(op.f('ix_rule_evaluation_log_campaign_id'), table_name='rule_evaluation_log')
    op.drop_table('rule_evaluation_log')