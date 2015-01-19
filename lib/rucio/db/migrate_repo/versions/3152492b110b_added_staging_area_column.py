# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Martin Barisits, <martin.barisits@cern.ch>, 2014

"""Added staging_area column

Revision ID: 3152492b110b
Revises: 22cf51430c78
Create Date: 2014-06-18 18:37:44.586999

"""

# revision identifiers, used by Alembic.
revision = '3152492b110b'
down_revision = '22cf51430c78'

import sqlalchemy as sa

from alembic import context, op


def upgrade():
    if context.get_context().dialect.name != 'sqlite':
        op.add_column('rses', sa.Column('staging_area', sa.Boolean(name='RSE_STAGING_AREA_CHK'), default=False))

    if context.get_context().dialect.name not in ('sqlite', 'mysql'):
        op.drop_constraint('REQUESTS_TYPE_CHK', 'requests', type_='check')
        op.create_check_constraint(name='REQUESTS_TYPE_CHK', source='requests', condition="request_type in ('U', 'D', 'T', 'I', '0')")


def downgrade():
    if context.get_context().dialect.name not in ('sqlite', 'mysql'):
        op.drop_constraint('RSE_STAGING_AREA_CHK', 'rses', type_='check')
        op.drop_constraint('REQUESTS_TYPE_CHK', 'requests', type_='check')
        op.create_check_constraint(name='REQUESTS_TYPE_CHK', source='requests', condition="request_type in ('U', 'D', 'T')")
    op.drop_column('rses', 'staging_area')
