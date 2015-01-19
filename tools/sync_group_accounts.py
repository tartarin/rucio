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
    f = open ('tools/atlas_groups.csv')
    for line in f.readlines():
         group = line.rstrip()
         info.append(group)
    f.close()

    c = Client()
    for group in info:
        try:
            account = group.split('.')[1]
            c.add_account(account=account, type='GROUP')
        except Duplicate:
           print 'Account %(account)s already added' % locals()

        try:
            c.add_scope(account, scope=group)
        except Duplicate:
           print 'Scope %(group)s already added' % locals()