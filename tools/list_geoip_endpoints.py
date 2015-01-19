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
import socket
import sys
import traceback
import urlparse
import os.path

import requests
import pygeoip

from rucio.client import Client

UNKNOWN = 3
CRITICAL = 2
WARNING = 1
OK = 0

if __name__ == '__main__':

    url = 'http://atlas-agis-api.cern.ch/request/ddmendpoint/query/list/?json'
    resp = requests.get(url=url)
    data = json.loads(resp.content)
    gi = pygeoip.GeoIP('GeoLiteCity.dat')
    giOrg = pygeoip.GeoIP('GeoIPOrg.dat')
    rses = ['PRAGUELCG2_DATADISK_RUCIOTEST', 'LRZ-LMU_DATADISK_RUCIOTEST', 'IN2P3-CPPM_DATADISK_RUCIOTEST',
            'NIKHEF-ELPROD_DATADISK_RUCIOTEST', 'PSNC_DATADISK_DATADISK_RUCIOTEST', 'UNI-FREIBURG_DATADISK_RUCIOTEST',
            'NDGF-T1_DATADISK_RUCIOTEST']

    c = Client()
    for rse in data:

        if rse['state']!='ACTIVE':
            continue


        if rse['name'] not in rses:
            continue

#         try:
#             deterministic = True
#             volatile = False
#             c.add_rse(rse=rse['name'], deterministic=deterministic, volatile=volatile)
#         except:
#             errno, errstr = sys.exc_info()[:2]
#             trcbck = traceback.format_exc()
#             print 'Interrupted processing with %s %s %s.' % (errno, errstr, trcbck)

        site = rse["rc_site"]
        for protocol in rse['protocols']:
            o = urlparse.urlparse(protocol)

            if o.scheme in ('srm'):
                url = o.netloc
                if o.port and str(o.port) in o.netloc:
                    url = o.netloc[:-len(str(o.port))-1]
                try:
                    ip = socket.gethostbyname(url)
                except socket.gaierror, e:
                    print e
                    continue

                geoip_data = gi.record_by_addr(ip)
#                org = giOrg.org_by_addr(ip)
#                print rse['name'], org
#                break
                rse_attributes = ['city', 'region_code', 'time_zone', 'country_name', 'continent']
                for rse_attr in rse_attributes:
                    if geoip_data[rse_attr]:
                        try:
#                            c.add_rse_attribute(rse['name'], rse_attr, geoip_data[rse_attr])
                            print rse['name'], socket.gethostbyname(url), rse_attr, geoip_data[rse_attr]
                        except:
                            errno, errstr = sys.exc_info()[:2]
                            trcbck = traceback.format_exc()