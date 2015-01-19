# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Martin Barisits, <martin.barisits@cern.ch>, 2014

"""Added share to rules

Revision ID: 52fd9f4916fa
Revises: 4a2cbedda8b9
Create Date: 2014-07-15 17:57:58.189448

"""

# revision identifiers, used by Alembic.
revision = '52fd9f4916fa'
down_revision = '4a2cbedda8b9'

from alembic import context, op
import sqlalchemy as sa


def upgrade():
    op.add_column('rules', sa.Column('activity', sa.String(50)))


def downgrade():
    if context.get_context().dialect.name != 'sqlite':
        op.drop_column('rules', 'activity')
