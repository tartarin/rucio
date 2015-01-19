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

    user     = 'ATLAS_RUCIO_TEST'
    password = 'RUC4tst187'
    dsn = '(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=intr1-v.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=intr2-v.cern.ch)(PORT=10121)))(LOAD_BALANCE=yes)(CONNECT_DATA=(SERVICE_NAME=INTR.CERN.CH)))'

    rses = [u'BNL-OSG2_DATADISK', u'BNL-OSG2_DATATAPE', u'BNL-OSG2_DDMTEST', u'BNL-OSG2_DET-SLHC', u'BNL-OSG2_HOTDISK', u'BNL-OSG2_LOCALGROUPDISK', u'BNL-OSG2_MCTAPE', u'BNL-OSG2_PERF-EGAMMA', u'BNL-OSG2_PERF-FLAVTAG', u'BNL-OSG2_PERF-JETS', u'BNL-OSG2_PERF-MUONS', u'BNL-OSG2_PHYS-HI', u'BNL-OSG2_PHYS-SM', u'BNL-OSG2_PHYS-TOP', u'BNL-OSG2_PRODDISK', u'BNL-OSG2_SCRATCHDISK', u'BNL-OSG2_TRIG-DAQ', u'BNL-OSG2_USERDISK']
    try:
        connection = cx_Oracle.connect(user, password, dsn)
        cursor = connection.cursor()
        data.reverse()
        for rse in data:
            try:

                if rse['state']!='ACTIVE' or 'RUCIOTEST' in rse['name']:
                    continue


                if rse['name'] in rses:

                    print 'Import replicas for %(name)s' % rse
                    # get rse_id
                    rse_id = None
                    query = '''select rawtohex(id) from atlas_rucio_test.rses where rse='%(name)s' ''' % rse
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
                            subquery = '''select  hextoraw('%(rse_id)s') as rse_id, substr(sfn, instr(sfn, '/', -1) + 1) as name, 1 as is_migrated, sfn, null as path from cns_file_replica@ATLLFCBNLT1.BNL.GOV  where (sfn like '%(short_surl)s'||'%%' OR sfn like '%(long_surl)s'||'%%') ''' % locals()
                            if rse['is_tape']:
                                subquery = '''select hextoraw('%(rse_id)s') as rse_id, case when INSTR(substr(sfn, instr(sfn, '/', -1) + 1),'__DQ2')> 0 then SUBSTR(substr(sfn, instr(sfn, '/', -1) + 1), 1, INSTR(substr(sfn, instr(sfn, '/', -1) + 1), '__DQ2')-1)  else substr(sfn, instr(sfn, '/', -1) + 1) end as name, 1 as is_migrated, sfn, replace(replace(sfn, '%(long_surl)s'), '%(short_surl)s')  as path from  cns_file_replica@ATLLFCBNLT1.BNL.GOV   where (sfn like '%(short_surl)s'||'%%' OR sfn like '%(long_surl)s'||'%%') ''' % locals()
                            subquery = subquery.replace("/'||'%'", "/%'")
                            query = '''INSERT INTO atlas_rucio_test.TMP_REPLICAS(rse_id, name, is_migrated, sfn, path) %(subquery)s''' % locals()
#                            query = '''MERGE INTO atlas_rucio_test.tmp_replicas t USING (%(subquery)s) r ON (t.rse_id = r.rse_id AND t.name = r.name) WHEN NOT MATCHED THEN INSERT (rse_id, name, is_migrated, sfn, path) values (r.rse_id, r.name, 1, r.sfn, r.path)''' % locals()
                            print query
                            start = time.time()
                            # cursor.execute('ALTER SESSION SET PARALLEL_FORCE_LOCAL = TRUE')
                            #cursor.execute(query)
                            #print rse['name'], cursor.rowcount, time.time()-start
                            #connection.commit()
            except:
                errno, errstr = sys.exc_info()[:2]
                trcbck = traceback.format_exc()
                print 'Interrupted processing with %s %s %s.' % (errno, errstr, trcbck)
    finally:
        cursor.close()
        connection.close()
    sys.exit(0)
