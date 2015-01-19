#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#                       http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2014


import json
import sys
import traceback
import urlparse
import time

import cx_Oracle
import requests

if __name__ == '__main__':

    url = 'http://atlas-agis-api.cern.ch/request/ddmendpoint/query/list/?json'
    resp = requests.get(url=url)
    data = json.loads(resp.content)

    user     = 'ATLAS_RUCIO_W'
    password = 'w_LS!tst4DDM'
    dsn = '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=adcr1-s.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr2-s.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr3-s.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr4-s.cern.ch)(PORT=10121))(LOAD_BALANCE=on)(ENABLE=BROKEN)(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=adcr_rucio.cern.ch)))'

    rses = [u'TR-10-ULAKBIM_LOCALGROUPDISK', u'TR-10-ULAKBIM_PRODDISK', u'TR-10-ULAKBIM_SCRATCHDISK']
#    for rse in rses:
#        print "dq2-set-location-status -e %s -p d -s auto -r 'Migration to Rucio done'" % rse
#    sys.exit(-1)
    try:
        connection = cx_Oracle.connect(user, password, dsn)
        cursor = connection.cursor()
        for rse in data:
            try:

                if rse['state']!='ACTIVE' or 'RUCIOTEST' in rse['name']:
                    continue

                #if rse['is_tape']:
                #    continue
#                if rse['name'].startswith('LRZ-LMU') or rse['name'].startswith('INFN-FRASCATI'):
#                if rse['name'].startswith('IN2P3-LAPP_'):
#                if rse['name'] in rses:
#                if rse['name'].startswith('IN2P3-CC_'):
                if rse['name'] in rses:

                    print 'Import replicas for %(name)s' % rse
                    # get rse_id
                    rse_id = None
                    query = '''select rawtohex(id) from atlas_rucio.rses where rse='%(name)s' ''' % rse
                    for row in cursor.execute(query):
                        rse_id = row[0]

                    if not rse_id:
                        print 'RSE %(name)s is not registered in Rucio' % rse
                        continue

                    #if not rse['servedlfc'].startswith('lfc://prod-lfc-atlas.cern.ch'):
                    #    print 'RSE %(name)s in US LFCs' % rse
                    #    continue

                    for protocol in rse['protocols']:
                        o = urlparse.urlparse(protocol)
                        if o.scheme == 'srm':
                            web_service_path = o.path + '?' + o.query
                            host = o.netloc
                            prefix = rse['endpoint']

                            postfix = 'rucio/'
                            if rse['is_tape']:
                                postfix = ''

                            # compute surl formats
                            short_surl = o.scheme + '://' +  o.netloc.replace (':'+str(o.port), '') + rse['endpoint'] + postfix
                            long_surl = o.scheme + '://' + host + web_service_path + rse['endpoint'] + postfix
                            long_surl = long_surl.replace('SFN=?', 'SFN=')
                            # @ADCR_ADG.CERN.CH
                            subquery = '''select  hextoraw('%(rse_id)s') as rse_id, substr(sfn, instr(sfn, '/', -1) + 1) as name, 1 as is_migrated, sfn, null as path from atlas_lfc.cns_file_replica_VIEW@ADCR_ADG.CERN.CH  where (sfn like '%(short_surl)s'||'%%' OR sfn like '%(long_surl)s'||'%%') ''' % locals()
                            if rse['is_tape']:
                                subquery = '''select hextoraw('%(rse_id)s') as rse_id, case when INSTR(substr(sfn, instr(sfn, '/', -1) + 1),'__DQ2')> 0 then SUBSTR(substr(sfn, instr(sfn, '/', -1) + 1), 1, INSTR(substr(sfn, instr(sfn, '/', -1) + 1), '__DQ2')-1)  else substr(sfn, instr(sfn, '/', -1) + 1) end as name, 1 as is_migrated, sfn, replace(replace(sfn, '%(long_surl)s'), '%(short_surl)s')  as path from atlas_lfc.cns_file_replica_VIEW@ADCR_ADG.CERN.CH  where (sfn like '%(short_surl)s'||'%%' OR sfn like '%(long_surl)s'||'%%') ''' % locals()
                            subquery = subquery.replace("/'||'%'", "/%'")
                            query = '''INSERT INTO atlas_rucio.TMP_REPLICAS(rse_id, name, is_migrated, sfn, path) %(subquery)s''' % locals()
                            query = '''MERGE INTO atlas_rucio.tmp_replicas t USING (%(subquery)s) r ON (t.rse_id = r.rse_id AND t.name = r.name) WHEN NOT MATCHED THEN INSERT (rse_id, name, is_migrated, sfn, path) values (r.rse_id, r.name, 1, r.sfn, r.path)''' % locals()
                            print query
                            start = time.time()
                            # cursor.execute('ALTER SESSION SET PARALLEL_FORCE_LOCAL = TRUE')
#                            cursor.execute('ALTER SESSION SET STANDBY_MAX_DATA_DELAY = 5000') 
                            cursor.execute(query)
                            print rse['name'], 'OK',cursor.rowcount, time.time()-start
                            connection.commit()
            except:
                print rse['name'], 'KO'
                errno, errstr = sys.exc_info()[:2]
                trcbck = traceback.format_exc()
                print 'Interrupted processing with %s %s %s.' % (errno, errstr, trcbck)
    finally:
        cursor.close()
        connection.close()
    sys.exit(0)

