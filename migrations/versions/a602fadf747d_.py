"""empty message

Revision ID: a602fadf747d
Revises: de04c08b6033
Create Date: 2018-03-21 15:31:52.920802

"""
import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from app.models import USER_TYPES

revision = 'a602fadf747d'
down_revision = 'de04c08b6033'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('occupation', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('phone', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('type', sqlalchemy_utils.types.choice.ChoiceType(USER_TYPES), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'type')
    op.drop_column('user', 'phone')
    op.drop_column('user', 'occupation')
    op.drop_column('user', 'name')
    # ### end Alembic commands ###
