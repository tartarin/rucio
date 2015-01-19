# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Martin Barisits, <martin.barisits@cern.ch>, 2014

"""Added unique constraint to rules

Revision ID: 25fc855625cf
Revises: 4a7182d9578b
Create Date: 2014-11-24 15:38:21.056569

"""

# revision identifiers, used by Alembic.
revision = '25fc855625cf'
down_revision = '4a7182d9578b'

from alembic import op


def upgrade():
    op.create_unique_constraint('RULES_SC_NA_AC_RS_CO_UQ_IDX', 'rules', ['scope', 'name', 'account', 'rse_expression', 'copies'])


def downgrade():
    op.drop_constraint('RULES_SC_NA_AC_RS_CO_UQ_IDX', 'rules', type_='unique')
