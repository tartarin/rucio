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

import json

import os
import os.path
import sys
import traceback
import urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

class TLSv1HttpAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

UNKNOWN = 3
CRITICAL = 2
WARNING = 1
OK = 0

if __name__ == '__main__':

    url = 'http://atlas-agis-api.cern.ch/request/ddmendpoint/query/list/?json'
    resp = requests.get(url=url)
    data = json.loads(resp.content)


    rses = ['PRAGUELCG2_DATADISK_RUCIOTEST', 'LRZ-LMU_DATADISK_RUCIOTEST', 'IN2P3-CPPM_DATADISK_RUCIOTEST',
            'NIKHEF-ELPROD_DATADISK_RUCIOTEST', 'PSNC_DATADISK_DATADISK_RUCIOTEST', 'UNI-FREIBURG_DATADISK_RUCIOTEST',
            'NDGF-T1_DATADISK_RUCIOTEST']
    sites = {}
    for rse in data:

        if rse['state']!='ACTIVE' or rse['is_tape']:
            continue

        prefix = rse['endpoint']
        site = rse["rc_site"]

        if rse['name'] not in rses:
            continue

        for protocol in rse['protocols']:
            o = urlparse.urlparse(protocol)
            if o.scheme in ('http', 'https'):
                for permission, priority, path in rse['protocols'][protocol]:
                    break
                if site not in sites:
                    if o.path and o.path != u'/':
                        path = o.path + str(path)
                    sites[site] = o.scheme, o.netloc, path, prefix
                url = o.scheme + '://' + o.netloc

#                print urlparse.urljoin(url, path)
                url = urlparse.urljoin(url, prefix)
                print rse['name'], url
                #print rse['name'], url, path
                session = requests.Session()
                session.cert=os.getenv('X509_USER_PROXY')
                session.allow_redirects=True
                session.verify=False
                session.mount('https://', TLSv1HttpAdapter())
                try:
                    result = session.request('HEAD', url)
                    print result
                except requests.exceptions.SSLError, e:
                    print e
                except requests.exceptions.ConnectionError, e:
                    print e