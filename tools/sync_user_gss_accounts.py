#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#                       http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2013

from rucio.client import Client
from rucio.common.exception import Duplicate

if __name__ == '__main__':

    info = []
    f = open ('tools/atlas_gss_accounts.csv')
    for line in f.readlines():
        account, dn, email = line.rstrip().split('\t')
        info.append((account, dn, email))
    f.close()

#    f = open ('tools/gss_account_to_create.csv')
#    for line in f.readlines():
#        account, scope = line.rstrip().split('\t')
#        email = account + '@cern.ch'
#        dn = account + '@CERN.CH'
#        info.append((account, dn, email))
#    f.close()


    # info.reverse()
    c = Client()
    for account, dn, email in info:
        try:
            c.add_account(account=account, type='USER')
        except Duplicate:
           print 'Account %(account)s already added' % locals()

        try:
            c.add_identity(account=account, identity=dn, authtype='GSS', email=email , default=False)
        except Duplicate:
           print 'Identity %(account)s already added' % locals()

        try:
            scope = 'user.' + account
            c.add_scope(account, scope)
        except Duplicate:
           print 'Scope %(scope)s already added' % locals()