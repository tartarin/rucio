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
import sys
import traceback
import urlparse
import os.path

import requests

UNKNOWN = 3
CRITICAL = 2
WARNING = 1
OK = 0

if __name__ == '__main__':

    url = 'http://atlas-agis-api.cern.ch/request/ddmendpoint/query/list/?json'
    resp = requests.get(url=url)
    data = json.loads(resp.content)

    sites = {}
    for rse in data:

        if rse['state']!='ACTIVE' or rse['is_tape']:
            continue
        prefix = rse['endpoint']
        site = rse["rc_site"]

        for protocol in rse['protocols']:
            o = urlparse.urlparse(protocol)
            if o.scheme in ('http', 'https'):
                for permission, priority, path in rse['protocols'][protocol]:
                    break
                if site not in sites:
                    if o.path and o.path != u'/':
                        path = o.path + str(path)
                    sites[site] = o.scheme, o.netloc, path, prefix
                    # print site, protocol
                url = o.scheme + '://' + o.netloc
#                print rse['name'], url, path

#    for rse in data:
#        if rse['is_tape']:
#            continue
#        if not rse['is_deterministic'] and site in sites:
#            print rse['name']
#    sys.exit(-1)
    for rse in data:

        if rse['is_tape']:
            continue

        prefix = rse['endpoint']
        site = rse["rc_site"]
        if not any([urlparse.urlparse(protocol).scheme in ('http', 'https') for protocol in rse['protocols']]) and site in sites:
            scheme, host, path, p = sites[site]
            url = scheme + '://' + host
            if path == p:
                print rse['name'], url, prefix
            else:
                if host == 'lcg-door4.scinet.utoronto.ca:2880':
                    commonprefix = '/pnfs/scinet.utoronto.ca/data/atlas/atlas'
                    print rse['name'], url, p.replace(p[len(commonprefix):], prefix[len(commonprefix):])
                else:
                    commonprefix = os.path.commonprefix([p, prefix])
                    print rse['name'], url, path.replace(p[len(commonprefix):], prefix[len(commonprefix):])
