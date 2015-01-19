#!/bin/bash
# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#                       http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2013

echo 'Bootstrap production: Create root account'
python -c 'from rucio.db.util import create_root_account;create_root_account()'

echo 'Add ddmusr01 account'
rucio-admin account add --type SERVICE ddmusr01
rucio-admin identity add  --account ddmusr01 --type X509 --id '/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ddmadmin/CN=531497/CN=Robot: ATLAS Data Management'  --email ph-adp-ddm-lab@cern.ch

echo 'Sync rse_repository'
tools/sync_rses_with_agis.py

echo 'Sync ATLAS scopes'
tools/sync_scopes.py

echo 'Sync ATLAS user accounts/scopes'
tools/sync_user_accounts.py

echo 'Sync ATLAS user GSS accounts/scopes'
tools/sync_user_gss_accounts.py


echo 'Sync ATLAS group accounts/scopes'
tools/sync_group_accounts.py