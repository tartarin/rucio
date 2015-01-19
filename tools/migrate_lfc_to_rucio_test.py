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

#    user     = 'ATLAS_LFC_R'
#    password = 'afcrap4GA'
#    dsn = '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=adcr1-v.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr2-v.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr3-v.cern.ch)(PORT=10121))(ENABLE=BROKEN)(LOAD_BALANCE=yes)(CONNECT_DATA=(SERVICE_NAME=adcr.cern.ch)(SERVER=DEDICATED)(FAILOVER_MODE=(TYPE=SELECT)(METHOD=BASIC)(RETRIES=200)(DELAY=15))))'

    user     = 'ATLAS_RUCIO_TEST'
    password = 'RUC4tst187'
    dsn = '(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=intr1-v.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=intr2-v.cern.ch)(PORT=10121)))(LOAD_BALANCE=yes)(CONNECT_DATA=(SERVICE_NAME=INTR.CERN.CH)))'

    rses = [u'RAL-LCG2_DATADISK', u'RAL-LCG2_DATATAPE', u'RAL-LCG2_HOTDISK', u'RAL-LCG2_MCTAPE', u'RAL-LCG2_PERF-JETS', u'RAL-LCG2_PHYS-BEAUTY', u'RAL-LCG2_PHYS-EXOTICS', u'RAL-LCG2_SCRATCHDISK', u'UKI-LT2-BRUNEL_DATADISK', u'UKI-LT2-BRUNEL_PRODDISK', u'UKI-LT2-IC-HEP_DATADISK', u'UKI-LT2-IC-HEP_PRODDISK', u'UKI-LT2-QMUL-MWTEST_DATADISK', u'UKI-LT2-QMUL_DATADISK', u'UKI-LT2-QMUL_LOCALGROUPDISK', u'UKI-LT2-QMUL_PERF-JETS', u'UKI-LT2-QMUL_PHYS-TOP', u'UKI-LT2-QMUL_PRODDISK', u'UKI-LT2-QMUL_SCRATCHDISK', u'UKI-LT2-RHUL_DATADISK', u'UKI-LT2-RHUL_LOCALGROUPDISK', u'UKI-LT2-RHUL_PRODDISK', u'UKI-LT2-RHUL_SCRATCHDISK', u'UKI-LT2-UCL-HEP_DATADISK', u'UKI-LT2-UCL-HEP_LOCALGROUPDISK', u'UKI-LT2-UCL-HEP_PRODDISK', u'UKI-LT2-UCL-HEP_SCRATCHDISK', u'UKI-NORTHGRID-LANCS-HEP_DATADISK', u'UKI-NORTHGRID-LANCS-HEP_LOCALGROUPDISK', u'UKI-NORTHGRID-LANCS-HEP_PHYS-BEAUTY', u'UKI-NORTHGRID-LANCS-HEP_PHYS-TOP', u'UKI-NORTHGRID-LANCS-HEP_PRODDISK', u'UKI-NORTHGRID-LANCS-HEP_SCRATCHDISK', u'UKI-NORTHGRID-LIV-HEP_DATADISK', u'UKI-NORTHGRID-LIV-HEP_LOCALGROUPDISK', u'UKI-NORTHGRID-LIV-HEP_PERF-EGAMMA', u'UKI-NORTHGRID-LIV-HEP_PHYS-SUSY', u'UKI-NORTHGRID-LIV-HEP_PRODDISK', u'UKI-NORTHGRID-LIV-HEP_SCRATCHDISK', u'UKI-NORTHGRID-MAN-HEP_DATADISK', u'UKI-NORTHGRID-MAN-HEP_LOCALGROUPDISK', u'UKI-NORTHGRID-MAN-HEP_PRODDISK', u'UKI-NORTHGRID-MAN-HEP_SCRATCHDISK', u'UKI-NORTHGRID-SHEF-HEP_DATADISK', u'UKI-NORTHGRID-SHEF-HEP_LOCALGROUPDISK', u'UKI-NORTHGRID-SHEF-HEP_PRODDISK', u'UKI-NORTHGRID-SHEF-HEP_SCRATCHDISK', u'UKI-SCOTGRID-DURHAM_DATADISK', u'UKI-SCOTGRID-DURHAM_PRODDISK', u'UKI-SCOTGRID-ECDF-MWTEST_DATADISK', u'UKI-SCOTGRID-ECDF_DATADISK', u'UKI-SCOTGRID-ECDF_LOCALGROUPDISK', u'UKI-SCOTGRID-ECDF_PRODDISK', u'UKI-SCOTGRID-ECDF_SCRATCHDISK', u'UKI-SCOTGRID-ECDF_SOFT-SIMUL', u'UKI-SCOTGRID-GLASGOW_DATADISK', u'UKI-SCOTGRID-GLASGOW_IPV6TEST', u'UKI-SCOTGRID-GLASGOW_LOCALGROUPDISK', u'UKI-SCOTGRID-GLASGOW_PERF-IDTRACKING', u'UKI-SCOTGRID-GLASGOW_PHYS-SM', u'UKI-SCOTGRID-GLASGOW_PRODDISK', u'UKI-SCOTGRID-GLASGOW_SCRATCHDISK', u'UKI-SOUTHGRID-BHAM-HEP_DATADISK', u'UKI-SOUTHGRID-BHAM-HEP_LOCALGROUPDISK', u'UKI-SOUTHGRID-BHAM-HEP_PRODDISK', u'UKI-SOUTHGRID-BHAM-HEP_SCRATCHDISK', u'UKI-SOUTHGRID-CAM-HEP_DATADISK', u'UKI-SOUTHGRID-CAM-HEP_LOCALGROUPDISK', u'UKI-SOUTHGRID-CAM-HEP_PRODDISK', u'UKI-SOUTHGRID-CAM-HEP_SCRATCHDISK', u'UKI-SOUTHGRID-OX-HEP_DATADISK', u'UKI-SOUTHGRID-OX-HEP_IPV6TEST', u'UKI-SOUTHGRID-OX-HEP_LOCALGROUPDISK', u'UKI-SOUTHGRID-OX-HEP_PHYS-EXOTICS', u'UKI-SOUTHGRID-OX-HEP_PRODDISK', u'UKI-SOUTHGRID-OX-HEP_SCRATCHDISK', u'UKI-SOUTHGRID-RALPP_DATADISK', u'UKI-SOUTHGRID-RALPP_LOCALGROUPDISK', u'UKI-SOUTHGRID-RALPP_PHYS-HIGGS', u'UKI-SOUTHGRID-RALPP_PRODDISK', u'UKI-SOUTHGRID-RALPP_SCRATCHDISK', u'UKI-SOUTHGRID-SUSX_DATADISK', u'UKI-SOUTHGRID-SUSX_LOCALGROUPDISK', u'UKI-SOUTHGRID-SUSX_PRODDISK', u'UKI-SOUTHGRID-SUSX_SCRATCHDISK']
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
                            subquery = '''select  hextoraw('%(rse_id)s') as rse_id, substr(sfn, instr(sfn, '/', -1) + 1) as name, 1 as is_migrated, sfn, null as path from atlas_lfc.cns_file_replica_VIEW@ADCR_ADG.CERN.CH  where (sfn like '%(short_surl)s'||'%%' OR sfn like '%(long_surl)s'||'%%') ''' % locals()
                            if rse['is_tape']:
                                subquery = '''select hextoraw('%(rse_id)s') as rse_id, case when INSTR(substr(sfn, instr(sfn, '/', -1) + 1),'__DQ2')> 0 then SUBSTR(substr(sfn, instr(sfn, '/', -1) + 1), 1, INSTR(substr(sfn, instr(sfn, '/', -1) + 1), '__DQ2')-1)  else substr(sfn, instr(sfn, '/', -1) + 1) end as name, 1 as is_migrated, sfn, replace(replace(sfn, '%(long_surl)s'), '%(short_surl)s')  as path from atlas_lfc.cns_file_replica_VIEW@ADCR_ADG.CERN.CH  where (sfn like '%(short_surl)s'||'%%' OR sfn like '%(long_surl)s'||'%%') ''' % locals()
                            subquery = subquery.replace("/'||'%'", "/%'")
                            query = '''INSERT INTO atlas_rucio_test.TMP_REPLICAS(rse_id, name, is_migrated, sfn, path) %(subquery)s''' % locals()
                            # query = '''MERGE INTO atlas_rucio.tmp_replicas t USING (%(subquery)s) r ON (t.rse_id = r.rse_id AND t.name = r.name) WHEN NOT MATCHED THEN INSERT (rse_id, name, is_migrated, sfn, path) values (r.rse_id, r.name, 1, r.sfn, r.path)''' % locals()
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

