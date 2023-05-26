"""initial_model

Revision ID: 8c96a8a4cd48
Revises: 
Create Date: 2023-02-11 16:04:55.531478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c96a8a4cd48'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('influencer',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('about', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('verified', sa.Boolean(), server_default='False', nullable=False),
    sa.Column('otp', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(), server_default='None', nullable=True),
    sa.Column('gender', sa.String(), server_default='None', nullable=True),
    sa.Column('niches', sa.String(), server_default='None', nullable=True),
    sa.Column('curr_page', sa.Integer(), server_default='None', nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('otp',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('influencer_id', sa.String(), nullable=False),
    sa.Column('otp', sa.Integer(), nullable=True),
    sa.Column('verified', sa.Boolean(), server_default='False', nullable=False),
    sa.ForeignKeyConstraint(['influencer_id'], ['influencer.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('otp')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('otp')
    op.drop_table('influencer')
    # ### end Alembic commands ###
