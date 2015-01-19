# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2014
# - Cedric Serfon, <cedric.serfon@cern.ch>, 2014

"""Add comment column for subscriptions

Revision ID: 70587619328
Revises: 4207be2fd914
Create Date: 2014-10-02 16:56:00.484159

"""

# revision identifiers, used by Alembic.
revision = '70587619328'
down_revision = '4207be2fd914'

from alembic import context, op
import sqlalchemy as sa


def upgrade():
    op.add_column('subscriptions', sa.Column('comments', sa.String(4000)))


def downgrade():
    if context.get_context().dialect.name != 'sqlite':
        op.drop_column('subscriptions', 'comments')
