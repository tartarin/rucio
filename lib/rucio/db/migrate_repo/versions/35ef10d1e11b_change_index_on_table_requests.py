# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2014

"""change index on table requests

Revision ID: 35ef10d1e11b
Revises: 3152492b110b
Create Date: 2014-06-20 09:01:52.704794

"""

# revision identifiers, used by Alembic.
revision = '35ef10d1e11b'
down_revision = '3152492b110b'

from alembic import op


def upgrade():
    op.create_index('REQUESTS_TYP_STA_UPD_IDX', 'requests', ["request_type", "state", "updated_at"])
    op.drop_index('REQUESTS_TYP_STA_CRE_IDX', 'requests')


def downgrade():
    op.create_index('REQUESTS_TYP_STA_CRE_IDX', 'requests', ["request_type", "state", "created_at"])
    op.drop_index('REQUESTS_TYP_STA_UPD_IDX', 'requests')
