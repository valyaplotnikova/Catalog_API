"""Initial migration

Revision ID: 865376f404ad
Revises: 
Create Date: 2025-04-16 09:28:52.347617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '865376f404ad'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products',
    sa.Column('uid', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('uid', name=op.f('pk_products'))
    )
    op.create_index(op.f('ix_products_uid'), 'products', ['uid'], unique=False)
    op.create_table('properties',
    sa.Column('uid', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('type', sa.Enum('list', 'int', name='property_type'), nullable=False),
    sa.PrimaryKeyConstraint('uid', name=op.f('pk_properties'))
    )
    op.create_index(op.f('ix_properties_uid'), 'properties', ['uid'], unique=False)
    op.create_table('product_property_ints',
    sa.Column('product_uid', sa.UUID(), nullable=False),
    sa.Column('property_uid', sa.UUID(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_uid'], ['products.uid'], name=op.f('fk_product_property_ints_product_uid_products')),
    sa.ForeignKeyConstraint(['property_uid'], ['properties.uid'], name=op.f('fk_product_property_ints_property_uid_properties')),
    sa.PrimaryKeyConstraint('product_uid', 'property_uid', name=op.f('pk_product_property_ints'))
    )
    op.create_table('property_values',
    sa.Column('uid', sa.UUID(), nullable=False),
    sa.Column('property_uid', sa.UUID(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['property_uid'], ['properties.uid'], name=op.f('fk_property_values_property_uid_properties')),
    sa.PrimaryKeyConstraint('uid', name=op.f('pk_property_values'))
    )
    op.create_index(op.f('ix_property_values_uid'), 'property_values', ['uid'], unique=False)
    op.create_table('product_property_values',
    sa.Column('product_uid', sa.UUID(), nullable=False),
    sa.Column('property_uid', sa.UUID(), nullable=False),
    sa.Column('value_uid', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['product_uid'], ['products.uid'], name=op.f('fk_product_property_values_product_uid_products')),
    sa.ForeignKeyConstraint(['property_uid'], ['properties.uid'], name=op.f('fk_product_property_values_property_uid_properties')),
    sa.ForeignKeyConstraint(['value_uid'], ['property_values.uid'], name=op.f('fk_product_property_values_value_uid_property_values')),
    sa.PrimaryKeyConstraint('product_uid', 'property_uid', name=op.f('pk_product_property_values'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product_property_values')
    op.drop_index(op.f('ix_property_values_uid'), table_name='property_values')
    op.drop_table('property_values')
    op.drop_table('product_property_ints')
    op.drop_index(op.f('ix_properties_uid'), table_name='properties')
    op.drop_table('properties')
    op.drop_index(op.f('ix_products_uid'), table_name='products')
    op.drop_table('products')
    # ### end Alembic commands ###
