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

    scopes = []
    f = open ('tools/scopes.csv')
    for line in f.readlines():
        scope = line.rstrip()
        scopes.append(scope)
    f.close()

    c = Client()
    for scope in scopes:
        try:
            c.add_scope('ddmusr01', scope)
        except Duplicate:
           print 'Scope %(scope)s already added' % locals()