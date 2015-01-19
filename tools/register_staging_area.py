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


from rucio.client import Client

UNKNOWN = 3
CRITICAL = 2
WARNING = 1
OK = 0

if __name__ == '__main__':

    url = 'http://atlas-agis-api.cern.ch/request/ddmendpoint/query/list/?json'
    resp = requests.get(url=url)
    data = json.loads(resp.content)

    c = Client()
    for rse in data:

        # if not rse['is_rucio']:
        #     continue

        if rse['state'] != 'ACTIVE':
            continue

        if not rse['is_tape']:
            continue

        if rse['name'].startswith('NDGF-T1-RUCIOTEST'):
            continue

        rse_name = None
        if rse['name'].startswith('BNL-OSG2_'):
            rse_name = 'BNL-OSG2_TAPE_STAGING'
        elif rse['name'].startswith('CERN-PROD'):
            rse_name = 'CERN-PROD_TAPE_STAGING'
        elif rse['name'].startswith('FZK-LCG2'):
            rse_name = 'FZK-LCG2_TAPE_STAGING'
        elif rse['name'].startswith('IN2P3-CC'):
            rse_name = 'IN2P3-CC_TAPE_STAGING'
        elif rse['name'].startswith('INFN-T1'):
            rse_name = 'INFN-T1_TAPE_STAGING'
        elif rse['name'].startswith('NDGF-T1'):
            rse_name = 'NDGF-T1_TAPE_STAGING'
        elif rse['name'].startswith('PIC'):
            rse_name = 'PIC_TAPE_STAGING'
        elif rse['name'].startswith('RAL-LCG2'):
            rse_name = 'RAL-LCG2_TAPE_STAGING'
        elif rse['name'].startswith('RRC-KI-T1'):
            rse_name = 'RRC-KI-T1_TAPE_STAGING'
        elif rse['name'].startswith('SARA-MATRIX'):
            rse_name = 'SARA-MATRIX_TAPE_STAGING'
        elif rse['name'].startswith('TAIWAN-LCG2'):
            rse_name = 'TAIWAN-LCG2_TAPE_STAGING'
        elif rse['name'].startswith('TRIUMF-LCG2'):
            rse_name = 'TRIUMF-LCG2_TAPE_STAGING'
        elif rse['name'].startswith('PRAGUELCG2_LOCALGROUPTAPE'):
            rse_name = 'PRAGUELCG2_TAPE_STAGING'

        try:
                print rse['name'], 'staging_area', rse_name
                c.add_rse_attribute(rse['name'], 'staging_buffer', rse_name)
            #c.add_rse_attribute('NDGF-T1-RUCIOTEST_DATATAPE', 'staging_area', 'NDGF-T1-RUCIOTEST_DATATAPE_STAGING')

        except:
            errno, errstr = sys.exc_info()[:2]
            trcbck = traceback.format_exc()
            print 'Interrupted processing with %s %s %s.' % (errno, errstr, trcbck)

    sys.exit(OK)
