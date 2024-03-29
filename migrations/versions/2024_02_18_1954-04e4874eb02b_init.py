"""init

Revision ID: 04e4874eb02b
Revises: 
Create Date: 2024-02-18 19:54:56.192708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04e4874eb02b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('project_name', sa.String(length=256), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('INITIATION', 'PLANNING', 'DESIGN', 'DEVELOPMENT', 'TESTING', 'READY', name='statuschoices'), server_default='Initiation', nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_title'), 'teams', ['title'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('first_name', sa.String(length=128), server_default='', nullable=False),
    sa.Column('last_name', sa.String(length=128), server_default='', nullable=False),
    sa.Column('hashed_password', sa.String(length=1024), nullable=False),
    sa.Column('position', sa.Enum('DEFAULT', 'FRONTEND', 'BACKEND', 'DESIGNER', 'PM', 'QA', name='position'), server_default='', nullable=False),
    sa.Column('contact', sa.Text(), server_default='', nullable=False),
    sa.Column('photo', sa.String(length=256), server_default='', nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_table('users_teams',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'team_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_teams')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_teams_title'), table_name='teams')
    op.drop_table('teams')
    # ### end Alembic commands ###
