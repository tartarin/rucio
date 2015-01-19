#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2013-2014
# - Mario Lassnig, <mario.lassnig@cern.ch>, 2014

import json
import os.path
import requests
import sys
import traceback
import urlparse


UNKNOWN = 3
CRITICAL = 2
WARNING = 1
OK = 0

if __name__ == '__main__':

    url = 'http://atlas-agis-api.cern.ch/request/ddmendpoint/query/list/?json'
    resp = requests.get(url=url)
    data = json.loads(resp.content)

    for rse in data:

        if rse['state'] != 'ACTIVE':
            continue

        if rse['cloud'] != 'IT':
            continue

        print rse['name']

    sys.exit(OK)
