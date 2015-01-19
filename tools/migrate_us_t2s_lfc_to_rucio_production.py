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
    rses = [u'ANLASC_DATADISK', u'ANLASC_PRODDISK', u'ANLASC_SCRATCHDISK', u'ANLASC_USERDISK', u'ILLINOISHEP_DATADISK', u'ILLINOISHEP_LOCALGROUPDISK', u'ILLINOISHEP_PRODDISK', u'ILLINOISHEP_USERDISK', u'MWT2_DATADISK', u'MWT2_UC_LOCALGROUPDISK', u'MWT2_UC_PERF-JETS', u'MWT2_UC_PERF-TAU', u'MWT2_UC_PHYS-HIGGS', u'MWT2_UC_PHYS-TOP', u'MWT2_UC_PRODDISK', u'MWT2_UC_SCRATCHDISK', u'MWT2_UC_TRIG-DAQ', u'MWT2_UC_USERDISK', u'NERSC_LOCALGROUPDISK', u'NERSC_SCRATCHDISK', u'NET2_DATADISK', u'NET2_LOCALGROUPDISK', u'NET2_PERF-MUONS', u'NET2_PHYS-EXOTICS', u'NET2_PHYS-TOP', u'NET2_PRODDISK', u'NET2_SCRATCHDISK', u'NET2_USERDISK', u'OUHEP_OSG_DATADISK', u'OUHEP_OSG_LOCALGROUPDISK', u'OUHEP_OSG_USERDISK', u'OU_OCHEP_SWT2_DATADISK', u'OU_OCHEP_SWT2_LOCALGROUPDISK', u'OU_OCHEP_SWT2_PRODDISK', u'OU_OCHEP_SWT2_SCRATCHDISK', u'OU_OCHEP_SWT2_USERDISK', u'SLACXRD_DATADISK', u'SLACXRD_LOCALGROUPDISK', u'SLACXRD_PERF-FLAVTAG', u'SLACXRD_PERF-IDTRACKING', u'SLACXRD_PERF-JETS', u'SLACXRD_PHYS-BEAUTY', u'SLACXRD_PHYS-SM', u'SLACXRD_PRODDISK', u'SLACXRD_SCRATCHDISK', u'SLACXRD_SOFT-SIMUL', u'SLACXRD_TRIG-DAQ', u'SLACXRD_USERDISK', u'SMU_LOCALGROUPDISK', u'SWT2_CPB_DATADISK', u'SWT2_CPB_DET-INDET', u'SWT2_CPB_LOCALGROUPDISK', u'SWT2_CPB_PERF-EGAMMA', u'SWT2_CPB_PHYS-SUSY', u'SWT2_CPB_PHYS-TOP', u'SWT2_CPB_PRODDISK', u'SWT2_CPB_SCRATCHDISK', u'SWT2_CPB_USERDISK', u'UPENN_LOCALGROUPDISK', u'UTA_SWT2_DATADISK', u'UTA_SWT2_PRODDISK', u'UTD-HEP-SE', u'WISC_LOCALGROUPDISK']
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
                    query = '''select rawtohex(id) from atlas_rucio.rses where rse='%(name)s' ''' % rse
                    for row in cursor.execute(query):
                        rse_id = row[0]

                    if not rse_id:
                        print 'RSE %(name)s is not registered in Rucio' % rse
                        continue

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
                            subquery = '''select  hextoraw('%(rse_id)s') as rse_id, substr(sfn, instr(sfn, '/', -1) + 1) as name, 1 as is_migrated, sfn, null as path from cns_file_replica@ATLFCREP.BNL.GOV  where (sfn like '%(short_surl)s'||'%%' OR sfn like '%(long_surl)s'||'%%') AND SFN not like  'srm://%%/rucio/panda/dis/%%' ''' % locals()
                            subquery = subquery.replace("/'||'%'", "/%'")
                            query = '''INSERT INTO atlas_rucio.TMP_REPLICAS(rse_id, name, is_migrated, sfn, path) %(subquery)s''' % locals()
#                            query = '''MERGE INTO atlas_rucio.tmp_replicas t USING (%(subquery)s) r ON (t.rse_id = r.rse_id AND t.name = r.name) WHEN NOT MATCHED THEN INSERT (rse_id, name, is_migrated, sfn, path) values (r.rse_id, r.name, 1, r.sfn, r.path)''' % locals()
                            print query
                            start = time.time()
                            # cursor.execute('ALTER SESSION SET PARALLEL_FORCE_LOCAL = TRUE')
                            cursor.execute(query)
                            print rse['name'], cursor.rowcount, time.time()-start
                            connection.commit()
            except:
                errno, errstr = sys.exc_info()[:2]
                trcbck = traceback.format_exc()
                print 'Interrupted processing with %s %s %s.' % (errno, errstr, trcbck)
    finally:
        cursor.close()
        connection.close()
    sys.exit(0)