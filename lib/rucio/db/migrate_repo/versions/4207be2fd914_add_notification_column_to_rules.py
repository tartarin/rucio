# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Martin Barisits, <martin.barisits@cern.ch>, 2014

"""Add notification column to rules

Revision ID: 4207be2fd914
Revises: 14ec5aeb64cf
Create Date: 2014-09-29 15:32:16.342473

"""

# revision identifiers, used by Alembic.
revision = '4207be2fd914'
down_revision = '14ec5aeb64cf'

from alembic import context, op
import sqlalchemy as sa

from rucio.db.constants import RuleNotification


def upgrade():
    op.add_column('rules', sa.Column('notification', RuleNotification.db_type(name='RULES_NOTIFICATION_CHK'), default=RuleNotification.NO))


def downgrade():
    if context.get_context().dialect.name not in ('sqlite', 'mysql'):
        op.drop_constraint('RULES_NOTIFICATION_CHK', 'rules', type_='check')
    op.drop_column('rules', 'notification')
