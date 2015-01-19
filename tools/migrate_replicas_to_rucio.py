#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2014

"""
Migration script
"""

import argparse
import signal
import threading

from rucio.db.session import get_session

graceful_stop = threading.Event()

def stop(signum=None, frame=None):
    graceful_stop.set()


def migrate(total_workers, worker_number):
    print 'Worker %(worker_number)s/%(total_workers)s' % locals()
    session = get_session()
    try:
        query = '''
DECLARE
       TYPE t_string IS TABLE OF VARCHAR2(255) INDEX BY PLS_INTEGER;
       TYPE t_dates IS TABLE OF TIMESTAMP INDEX BY PLS_INTEGER;
       TYPE t_numbers IS TABLE OF NUMBER INDEX BY PLS_INTEGER;
       TYPE t_uuids IS TABLE OF  RAW(16) INDEX BY PLS_INTEGER;
       TYPE t_paths IS TABLE OF VARCHAR2(1024) INDEX BY PLS_INTEGER;


       scopes    t_string;
       names     t_string;
       guids     t_uuids;
       rseids    t_uuids;
       filesizes t_numbers;
       filebytes t_numbers;
       adler32s  t_string;
       md5s      t_string;
       dates     t_dates;
       paths     t_paths;
       CURSOR f_cur IS  WITH r as (select   /*+ INDEX(TMP_REPLICAS TMP_REPLICAS_IDX) */ name, rse_id, path from atlas_rucio.tmp_replicas where is_migrated is not null and ORA_HASH(name, %s) = %s)
       select rse_id,
              f.scope,
              name,
              hextoraw(replace(guid, '-', '')),
              filesize,
              case when INSTR(checksum,'ad:', 1) >0 then replace(checksum, 'ad:', '') end,
              case when INSTR(checksum,'md5:', 1) >0 then replace(checksum, 'md5:', '') end,
              creationdate,
              path
       from atlas_dq2.t_10_files f, r
       where f.lfn=r.name and f.scope is not null;
-- _VIEW@ADCR_ADG.CERN.CH
BEGIN
  OPEN f_cur;
       LOOP

          FETCH f_cur BULK COLLECT INTO rseids, scopes, names, guids, filesizes, adler32s, md5s, dates, paths LIMIT 1;
          BEGIN

--           FORALL i IN 1 .. scopes.count
--               MERGE INTO atlas_rucio.DIDS D
--                USING DUAL
--                ON (D.scope = scopes(i) AND D.name = names(i))
--                WHEN NOT MATCHED THEN INSERT (SCOPE, NAME, ACCOUNT, DID_TYPE, IS_OPEN, MONOTONIC, HIDDEN, OBSOLETE, COMPLETE, IS_NEW, AVAILABILITY, SUPPRESSED, BYTES, LENGTH, MD5, ADLER32, EXPIRED_AT, DELETED_AT, EVENTS, GUID, PROJECT, DATATYPE, RUN_NUMBER, STREAM_NAME, PROD_STEP, VERSION, CAMPAIGN, UPDATED_AT, CREATED_AT)
--                VALUES (scopes(i), names(i), 'root', 'F', 0, 0, 0, 0, 0, NULL, 'A', 0, filesizes(i), 1, md5s(i), adler32s(i), '', '', Null, guids(i), '', '', Null, '', '', '', '', dates(i), dates(i));

--           FORALL i IN 1 .. names.COUNT
--                INSERT INTO atlas_rucio.REPLICAS F (SCOPE, NAME, RSE_ID, BYTES, MD5, ADLER32, STATE, LOCK_CNT, ACCESSED_AT, TOMBSTONE, PATH, UPDATED_AT, CREATED_AT)
--                VALUES (scopes(i), names(i), rseids(i), filesizes(i), md5s(i), adler32s(i), 'A', 0, '', '', paths(i), dates(i), dates(i));

          FORALL i IN 1 .. names.COUNT
                UPDATE atlas_rucio.tmp_replicas
                SET IS_MIGRATED = NULL
                WHERE rse_id =  rseids(i) and name = names(i);

--            FORALL i IN filesizes.first .. filesizes.last
--                INSERT INTO atlas_rucio.UPDATED_RSE_COUNTERS (ID, RSE_ID, FILES, BYTES, UPDATED_AT, CREATED_AT)
--                VALUES (SYS_GUID(), rseids(i), 1, filesizes(i),  sys_extract_utc(systimestamp),  sys_extract_utc(systimestamp));

--               UPDATE atlas_rucio.RSE_COUNTERS
--               SET files=files+1, bytes=bytes+filesizes(i), updated_at=sysdate
--               WHERE RSE_ID = rseids(i);

          COMMIT;
--        EXCEPTION
--                WHEN OTHERS THEN
--                 WHEN DUP_VAL_ON_INDEX THEN
--          FORALL i IN 1 .. names.COUNT
--                UPDATE atlas_rucio.tmp_replicas
--                SET IS_MIGRATED = NULL
--                WHERE rse_id =  rseids(i) and name = names(i);
        END;
       EXIT WHEN f_cur%%NOTFOUND;
       END LOOP;
  CLOSE f_cur;
END;''' % (total_workers, worker_number)
        session.execute(query)
    finally:
        session.close()
        print 'Worker %(worker_number)s/%(total_workers)s done' % locals()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--total-workers", action="store", default=1, type=int, help='Total number of workers per process')
    args = parser.parse_args()

    threads = list()

    for i in xrange(0, args.total_workers):
        kwargs = {'worker_number': i,
                  'total_workers': args.total_workers-1}
        threads.append(threading.Thread(target=migrate, kwargs=kwargs))

    [t.start() for t in threads]
    while threads[0].is_alive():
        [t.join(timeout=3.14) for t in threads]

