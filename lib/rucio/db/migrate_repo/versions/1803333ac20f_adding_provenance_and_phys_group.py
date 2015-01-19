# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2014
# - Cedric Serfon, <cedric.serfon@cern.ch>, 2015

"""Adding provenance and phys_group

Revision ID: 1803333ac20f
Revises: 4c3a4acfe006
Create Date: 2015-01-08 14:32:13.391135

"""

# revision identifiers, used by Alembic.
revision = '1803333ac20f'
down_revision = '4c3a4acfe006'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('dids', sa.Column('provenance', sa.String(2)))
    op.add_column('dids', sa.Column('phys_group', sa.String(25)))


def downgrade():
    op.drop_column('dids', 'provenance')
    op.drop_column('dids', 'phys_group')
