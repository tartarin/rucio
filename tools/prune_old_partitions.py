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
import time

import cx_Oracle


if __name__ == '__main__':

    accounts = []
    f = open('tools/atlas_user_gss.csv')
    for line in f.readlines():
        account, dn, email = line.rstrip().split('\t')
        accounts.append(account)
    f.close()

    info = []
    f = open ('tools/atlas_accounts.csv')
    for line in f.readlines():
        account, dn, email = line.rstrip().split('\t')
        if account not in accounts:
            accounts.append(account)
    f.close()

    user     = 'ATLAS_RUCIO'
    password = 'LS!tst4DDM'
    dsn = '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=adcr1-s.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr2-s.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr3-s.cern.ch)(PORT=10121))(ADDRESS=(PROTOCOL=TCP)(HOST=adcr4-s.cern.ch)(PORT=10121))(LOAD_BALANCE=on)(ENABLE=BROKEN)(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=adcr_rucio.cern.ch)))'
    try:
        connection = cx_Oracle.connect(user, password, dsn)
        cursor = connection.cursor()

        f = open('tools/atlas_gss_accounts.csv')
        lines = f.readlines()
#        lines.reverse()
        for line in lines:
            account, dn, email = line.rstrip().split('\t')
            if account not in accounts:
                account = account.upper()
                deletable = True
                for table in ('DIDS', 'DELETED_DIDS', 'REPLICAS', 'CONTENTS', 'LOCKS'):
                     try:
                         query = '''SELECT  1  FROM user_tab_partitions WHERE    partition_name = 'USER_%(account)s' AND table_name = '%(table)s' ''' % locals()
                         query = '''DELETE FROM LOGGING_TABPARTITIONS WHERE PARTITION_NAME = 'USER_%(account)s' ''' % locals()
                         print query
                         cursor.execute(query)
#                         if cursor.fetchone():
#                            deletable = False
#                            q = 'alter table %(table)s drop partition "USER_%(account)s"' % locals()
#                            cursor.execute(q)
#                            print q
                         connection.commit()
                     except:
                         errno, errstr = sys.exc_info()[:2]
                         trcbck = traceback.format_exc()
                         print trcbck

#                 for c in ('C', 'D', 'F'):
#                     try:
#                         query = '''SELECT 1 FROM user_tab_subpartitions WHERE  partition_name = 'USER_%(account)s_%(c)s' AND table_name = 'DIDS' ''' % locals()
# #                        print query
#                         cursor.execute(query)
#                         if cursor.fetchone():
#                             deletable = False
# #                            query = 'alter table DIDS drop subpartition "USER_%(account)s_%(c)s"' % locals()
# #                            print query
# #                            cursor.execute(query)
# #                            connection.commit()
#                     except:
#                          errno, errstr = sys.exc_info()[:2]
#                          trcbck = traceback.format_exc()
#                          print trcbck

#                if deletable:
#                    acc = account.lower()
#                    try:
#                       query =  '''delete from scopes where scope = 'user.%(acc)s' ''' % locals()
#                       query =  '''delete from identities where identity='%(acc)s@CERN.CH' ''' % locals()
#                       query = '''delete from account_map where identity='%(acc)s@CERN.CH' ''' % locals()
#                        query =  '''delete from accounts where account = '%(acc)s' ''' % locals()
#                        print query
#                        cursor.execute(query)
#                        connection.commit()
#                    except:
#                         errno, errstr = sys.exc_info()[:2]
#                         trcbck = traceback.format_exc()
#                         print trcbck

        f.close()
    finally:
        cursor.close()
        connection.close()