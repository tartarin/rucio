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

#    user     = 'ATLAS_RUCIO_W'
#    password = 'w_LS!tst4DDM'
#    dsn = '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=adcr1-s.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr2-s.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr3-s.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr4-s.cern.ch)(PORT=10121))(LOAD_BALANCE=on)(ENABLE=BROKEN)(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=adcr_rucio.cern.ch)))'

    rses = [u'BEIJING-LCG2_DATADISK', u'BEIJING-LCG2_LOCALGROUPDISK', u'BEIJING-LCG2_PRODDISK', u'GRIF-IRFU_DATADISK', u'GRIF-IRFU_LOCALGROUPDISK', u'GRIF-IRFU_PHYS-TOP', u'GRIF-IRFU_PRODDISK', u'GRIF-IRFU_SCRATCHDISK', u'GRIF-LAL_DATADISK', u'GRIF-LAL_LOCALGROUPDISK', u'GRIF-LAL_PHYS-SUSY', u'GRIF-LAL_PRODDISK', u'GRIF-LAL_SCRATCHDISK', u'GRIF-LPNHE_DATADISK', u'GRIF-LPNHE_LOCALGROUPDISK', u'GRIF-LPNHE_PERF-EGAMMA', u'GRIF-LPNHE_PRODDISK', u'GRIF-LPNHE_SCRATCHDISK', u'IN2P3-CPPM_DATADISK', u'IN2P3-CPPM_LOCALGROUPDISK', u'IN2P3-CPPM_PERF-FLAVTAG', u'IN2P3-CPPM_PRODDISK', u'IN2P3-CPPM_SCRATCHDISK', u'IN2P3-LPC_DATADISK', u'IN2P3-LPC_LOCALGROUPDISK', u'IN2P3-LPC_PHYS-TOP', u'IN2P3-LPC_PRODDISK', u'IN2P3-LPC_SCRATCHDISK', u'IN2P3-LPSC_DATADISK', u'IN2P3-LPSC_LOCALGROUPDISK', u'IN2P3-LPSC_PRODDISK', u'IN2P3-LPSC_SCRATCHDISK', u'RO-02-NIPNE_DATADISK', u'RO-02-NIPNE_LOCALGROUPDISK', u'RO-02-NIPNE_PRODDISK', u'RO-02-NIPNE_SCRATCHDISK', u'RO-07-NIPNE_DATADISK', u'RO-07-NIPNE_LOCALGROUPDISK', u'RO-07-NIPNE_PRODDISK', u'RO-07-NIPNE_SCRATCHDISK', u'RO-14-ITIM_DATADISK', u'RO-14-ITIM_PRODDISK', u'RO-16-UAIC_DATADISK', u'RO-16-UAIC_PRODDISK', u'RO-16-UAIC_SCRATCHDISK', u'TOKYO-LCG2_DATADISK', u'TOKYO-LCG2_DET-MUON', u'TOKYO-LCG2_LOCALGROUPDISK', u'TOKYO-LCG2_PERF-JETS', u'TOKYO-LCG2_PERF-MUONS', u'TOKYO-LCG2_PHYS-EXOTICS', u'TOKYO-LCG2_PHYS-HIGGS', u'TOKYO-LCG2_PHYS-SUSY', u'TOKYO-LCG2_PRODDISK', u'TOKYO-LCG2_SCRATCHDISK', u'TOKYO-LCG2_TRIG-DAQ', u'AUSTRALIA-ATLAS_DATADISK', u'AUSTRALIA-ATLAS_LOCALGROUPDISK', u'AUSTRALIA-ATLAS_PHYS-SM', u'AUSTRALIA-ATLAS_PRODDISK', u'AUSTRALIA-ATLAS_SCRATCHDISK', u'CA-MCGILL-CLUMEQ-T2_DATADISK', u'CA-MCGILL-CLUMEQ-T2_LOCALGROUPDISK', u'CA-MCGILL-CLUMEQ-T2_PHYS-HIGGS', u'CA-MCGILL-CLUMEQ-T2_PRODDISK', u'CA-MCGILL-CLUMEQ-T2_SCRATCHDISK', u'CA-SCINET-T2_DATADISK', u'CA-SCINET-T2_LOCALGROUPDISK', u'CA-SCINET-T2_PHYS-TOP', u'CA-SCINET-T2_PRODDISK', u'CA-SCINET-T2_SCRATCHDISK', u'CA-VICTORIA-WESTGRID-T2_DATADISK', u'CA-VICTORIA-WESTGRID-T2_LOCALGROUPDISK', u'CA-VICTORIA-WESTGRID-T2_PHYS-EXOTICS', u'CA-VICTORIA-WESTGRID-T2_PRODDISK', u'CA-VICTORIA-WESTGRID-T2_SCRATCHDISK', u'EELA-UTFSM_DATADISK', u'EELA-UTFSM_LOCALGROUPDISK', u'EELA-UTFSM_PRODDISK', u'EELA-UTFSM_SCRATCHDISK', u'IFAE_DATADISK', u'IFAE_LOCALGROUPDISK', u'IFAE_PHYS-TOP', u'IFAE_PRODDISK', u'IFAE_SCRATCHDISK', u'IFIC-LCG2_CALIBDISK', u'IFIC-LCG2_DATADISK', u'IFIC-LCG2_LOCALGROUPDISK', u'IFIC-LCG2_PHYS-EXOTICS', u'IFIC-LCG2_PHYS-SUSY', u'IFIC-LCG2_PRODDISK', u'IFIC-LCG2_SCRATCHDISK', u'LIP-COIMBRA_DATADISK', u'LIP-COIMBRA_LOCALGROUPDISK', u'LIP-COIMBRA_PRODDISK', u'LIP-COIMBRA_SCRATCHDISK', u'LIP-LISBON_LOCALGROUPDISK', u'NCG-INGRID-PT_DATADISK', u'NCG-INGRID-PT_PERF-JETS', u'NCG-INGRID-PT_PRODDISK', u'NCG-INGRID-PT_SCRATCHDISK', u'PIC_DATADISK', u'PIC_DATATAPE', u'PIC_HOTDISK', u'PIC_MCTAPE', u'PIC_PHYS-SM', u'PIC_SCRATCHDISK', u'SFU-LCG2_DATADISK', u'SFU-LCG2_LOCALGROUPDISK', u'SFU-LCG2_PERF-JETS', u'SFU-LCG2_PHYS-SM', u'SFU-LCG2_PRODDISK', u'SFU-LCG2_SCRATCHDISK', u'TRIUMF-LCG2_DATADISK', u'TRIUMF-LCG2_DATATAPE', u'TRIUMF-LCG2_HOTDISK', u'TRIUMF-LCG2_LOCALGROUPDISK', u'TRIUMF-LCG2_MCTAPE', u'TRIUMF-LCG2_PERF-JETS', u'TRIUMF-LCG2_PERF-TAU', u'TRIUMF-LCG2_SCRATCHDISK', u'UAM-LCG2_DATADISK', u'UAM-LCG2_LOCALGROUPDISK', u'UAM-LCG2_PHYS-HIGGS', u'UAM-LCG2_PRODDISK', u'UAM-LCG2_SCRATCHDISK']

    rses = [u'BEIJING-LCG2_DATADISK', u'BEIJING-LCG2_LOCALGROUPDISK', u'BEIJING-LCG2_PRODDISK', u'GRIF-IRFU_DATADISK', u'GRIF-IRFU_LOCALGROUPDISK', u'GRIF-IRFU_PHYS-TOP', u'GRIF-IRFU_PRODDISK', u'GRIF-IRFU_SCRATCHDISK', u'GRIF-LAL_DATADISK', u'GRIF-LAL_LOCALGROUPDISK', u'GRIF-LAL_PHYS-SUSY', u'GRIF-LAL_PRODDISK', u'GRIF-LAL_SCRATCHDISK', u'GRIF-LPNHE_DATADISK', u'GRIF-LPNHE_LOCALGROUPDISK', u'GRIF-LPNHE_PERF-EGAMMA', u'GRIF-LPNHE_PRODDISK', u'GRIF-LPNHE_SCRATCHDISK', u'IN2P3-CPPM_DATADISK', u'IN2P3-CPPM_LOCALGROUPDISK', u'IN2P3-CPPM_PERF-FLAVTAG', u'IN2P3-CPPM_PRODDISK', u'IN2P3-CPPM_SCRATCHDISK', u'IN2P3-LPC_DATADISK', u'IN2P3-LPC_LOCALGROUPDISK', u'IN2P3-LPC_PHYS-TOP', u'IN2P3-LPC_PRODDISK', u'IN2P3-LPC_SCRATCHDISK', u'IN2P3-LPSC_DATADISK', u'IN2P3-LPSC_LOCALGROUPDISK', u'IN2P3-LPSC_PRODDISK', u'IN2P3-LPSC_SCRATCHDISK', u'RO-02-NIPNE_DATADISK', u'RO-02-NIPNE_LOCALGROUPDISK', u'RO-02-NIPNE_PRODDISK', u'RO-02-NIPNE_SCRATCHDISK', u'RO-07-NIPNE_DATADISK', u'RO-07-NIPNE_LOCALGROUPDISK', u'RO-07-NIPNE_PRODDISK', u'RO-07-NIPNE_SCRATCHDISK', u'RO-14-ITIM_DATADISK', u'RO-14-ITIM_PRODDISK', u'RO-16-UAIC_DATADISK', u'RO-16-UAIC_PRODDISK', u'RO-16-UAIC_SCRATCHDISK', u'TOKYO-LCG2_DATADISK', u'TOKYO-LCG2_DET-MUON', u'TOKYO-LCG2_LOCALGROUPDISK', u'TOKYO-LCG2_PERF-JETS', u'TOKYO-LCG2_PERF-MUONS', u'TOKYO-LCG2_PHYS-EXOTICS', u'TOKYO-LCG2_PHYS-HIGGS', u'TOKYO-LCG2_PHYS-SUSY', u'TOKYO-LCG2_PRODDISK', u'TOKYO-LCG2_SCRATCHDISK', u'TOKYO-LCG2_TRIG-DAQ']
    rses = [u'AUSTRALIA-ATLAS_DATADISK', u'AUSTRALIA-ATLAS_LOCALGROUPDISK', u'AUSTRALIA-ATLAS_PHYS-SM', u'AUSTRALIA-ATLAS_PRODDISK', u'AUSTRALIA-ATLAS_SCRATCHDISK', u'CA-MCGILL-CLUMEQ-T2_DATADISK', u'CA-MCGILL-CLUMEQ-T2_LOCALGROUPDISK', u'CA-MCGILL-CLUMEQ-T2_PHYS-HIGGS', u'CA-MCGILL-CLUMEQ-T2_PRODDISK', u'CA-MCGILL-CLUMEQ-T2_SCRATCHDISK', u'CA-SCINET-T2_DATADISK', u'CA-SCINET-T2_LOCALGROUPDISK', u'CA-SCINET-T2_PHYS-TOP', u'CA-SCINET-T2_PRODDISK', u'CA-SCINET-T2_SCRATCHDISK', u'CA-VICTORIA-WESTGRID-T2_DATADISK', u'CA-VICTORIA-WESTGRID-T2_LOCALGROUPDISK', u'CA-VICTORIA-WESTGRID-T2_PHYS-EXOTICS', u'CA-VICTORIA-WESTGRID-T2_PRODDISK', u'CA-VICTORIA-WESTGRID-T2_SCRATCHDISK', u'EELA-UTFSM_DATADISK', u'EELA-UTFSM_LOCALGROUPDISK', u'EELA-UTFSM_PRODDISK', u'EELA-UTFSM_SCRATCHDISK', u'IFAE_DATADISK', u'IFAE_LOCALGROUPDISK', u'IFAE_PHYS-TOP', u'IFAE_PRODDISK', u'IFAE_SCRATCHDISK', u'IFIC-LCG2_CALIBDISK', u'IFIC-LCG2_DATADISK', u'IFIC-LCG2_LOCALGROUPDISK', u'IFIC-LCG2_PHYS-EXOTICS', u'IFIC-LCG2_PHYS-SUSY', u'IFIC-LCG2_PRODDISK', u'IFIC-LCG2_SCRATCHDISK', u'LIP-COIMBRA_DATADISK', u'LIP-COIMBRA_LOCALGROUPDISK', u'LIP-COIMBRA_PRODDISK', u'LIP-COIMBRA_SCRATCHDISK', u'LIP-LISBON_LOCALGROUPDISK', u'NCG-INGRID-PT_DATADISK', u'NCG-INGRID-PT_PERF-JETS', u'NCG-INGRID-PT_PRODDISK', u'NCG-INGRID-PT_SCRATCHDISK', u'PIC_DATADISK', u'PIC_DATATAPE', u'PIC_HOTDISK', u'PIC_MCTAPE', u'PIC_PHYS-SM', u'PIC_SCRATCHDISK', u'SFU-LCG2_DATADISK', u'SFU-LCG2_LOCALGROUPDISK', u'SFU-LCG2_PERF-JETS', u'SFU-LCG2_PHYS-SM', u'SFU-LCG2_PRODDISK', u'SFU-LCG2_SCRATCHDISK', u'TRIUMF-LCG2_DATADISK', u'TRIUMF-LCG2_DATATAPE', u'TRIUMF-LCG2_HOTDISK', u'TRIUMF-LCG2_LOCALGROUPDISK', u'TRIUMF-LCG2_MCTAPE', u'TRIUMF-LCG2_PERF-JETS', u'TRIUMF-LCG2_PERF-TAU', u'TRIUMF-LCG2_SCRATCHDISK', u'UAM-LCG2_DATADISK', u'UAM-LCG2_LOCALGROUPDISK', u'UAM-LCG2_PHYS-HIGGS', u'UAM-LCG2_PRODDISK', u'UAM-LCG2_SCRATCHDISK']
    rses = (u'TRIUMF-LCG2_DATADISK', u'TRIUMF-LCG2_DATATAPE', u'UAM-LCG2_DATADISK')
    rses = [u'TR-10-ULAKBIM_LOCALGROUPDISK', u'TR-10-ULAKBIM_PRODDISK', u'TR-10-ULAKBIM_SCRATCHDISK']
    try:
        connection = cx_Oracle.connect(user, password, dsn)
        cursor = connection.cursor()
        data.reverse()
        for rse in data:
            try:

                if rse['state']!='ACTIVE' or 'RUCIOTEST' in rse['name']:
                    continue

#                if not rse['is_tape']:
#                    continue
#                if rse['name'].startswith('LRZ-LMU') or rse['name'].startswith('INFN-FRASCATI'):
#                if rse['name'].startswith('IN2P3-LAPP_'):
#                if rse['name'].startswith('TAIWAN-LCG2')):

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
                            print subquery
                            query = '''INSERT INTO atlas_rucio_test.TMP_REPLICAS(rse_id, name, is_migrated, sfn, path) %(subquery)s''' % locals()
#                            query = '''MERGE INTO atlas_rucio_test.tmp_replicas t USING (%(subquery)s) r ON (t.rse_id = r.rse_id AND t.name = r.name) WHEN NOT MATCHED THEN INSERT (rse_id, name, is_migrated, sfn, path) values (r.rse_id, r.name, 1, r.sfn, r.path)''' % locals()
                            #print query
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
