"""empty message

Revision ID: e77c195b985b
Revises: 
Create Date: 2021-04-29 22:46:18.133390

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e77c195b985b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=80), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('audio_favorite',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('en', sa.String(length=50), nullable=False),
    sa.Column('cnt', sa.String(length=50), nullable=False),
    sa.Column('loc', sa.String(length=200), nullable=False),
    sa.Column('time', sa.String(length=50), nullable=False),
    sa.Column('url_sound', sa.String(length=200), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bird_capture',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('en', sa.String(length=50), nullable=False),
    sa.Column('cnt', sa.String(length=50), nullable=False),
    sa.Column('loc', sa.String(length=200), nullable=False),
    sa.Column('time', sa.String(length=50), nullable=False),
    sa.Column('rmk', sa.String(length=300), nullable=False),
    sa.Column('public', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bird_capture')
    op.drop_table('audio_favorite')
    op.drop_table('user')
    # ### end Alembic commands ###
