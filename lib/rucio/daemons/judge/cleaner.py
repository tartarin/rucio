# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Martin Barisits, <martin.barisits@cern.ch>, 2013-2015
# - Mario Lassnig, <mario.lassnig@cern.ch>, 2013

"""
Judge-Cleaner is a daemon to clean expired replication rules.
"""

import logging
import ntplib
import sys
import threading
import time
import traceback

from copy import deepcopy
from datetime import datetime, timedelta
from re import match
from random import randint

from sqlalchemy.exc import DatabaseError

from rucio.common.config import config_get
from rucio.common.exception import DatabaseException, AccessDenied
from rucio.core.rule import delete_rule, get_expired_rules
from rucio.core.monitor import record_gauge, record_counter

graceful_stop = threading.Event()

logging.basicConfig(stream=sys.stdout,
                    level=getattr(logging, config_get('common', 'loglevel').upper()),
                    format='%(asctime)s\t%(process)d\t%(levelname)s\t%(message)s')


def rule_cleaner(once=False, process=0, total_processes=1, thread=0, threads_per_process=1):
    """
    Main loop to check for expired replication rules
    """

    logging.info('rule_cleaner: starting')

    logging.info('rule_cleaner: started')

    paused_rules = {}  # {rule_id: datetime}

    while not graceful_stop.is_set():
        try:
            start = time.time()
            rules = get_expired_rules(total_workers=total_processes*threads_per_process-1,
                                      worker_number=process*threads_per_process+thread,
                                      limit=1000)
            logging.debug('rule_cleaner index query time %f fetch size is %d' % (time.time() - start, len(rules)))

            # Refresh paused rules
            iter_paused_rules = deepcopy(paused_rules)
            for key in iter_paused_rules:
                if datetime.utcnow() > paused_rules[key]:
                    del paused_rules[key]

            # Remove paused rules from result set
            rules = [rule for rule in rules if rule[0] not in paused_rules]

            if not rules and not once:
                logging.info('rule_cleaner[%s/%s] did not get any work' % (process*threads_per_process+thread, total_processes*threads_per_process-1))
                time.sleep(10)
            else:
                record_gauge('rule.judge.cleaner.threads.%d' % (process*threads_per_process+thread), 1)
                for rule in rules:
                    rule_id = rule[0]
                    rule_expression = rule[1]
                    logging.info('rule_cleaner[%s/%s]: Deleting rule %s with expression %s' % (process*threads_per_process+thread, total_processes*threads_per_process-1, rule_id, rule_expression))
                    if graceful_stop.is_set():
                        break
                    try:
                        start = time.time()
                        delete_rule(rule_id=rule_id, nowait=True)
                        logging.debug('rule_cleaner[%s/%s]: deletion of %s took %f' % (process*threads_per_process+thread, total_processes*threads_per_process-1, rule_id, time.time() - start))
                    except (DatabaseException, DatabaseError, AccessDenied), e:
                        if isinstance(e.args[0], tuple):
                            if match('.*ORA-00054.*', e.args[0][0]):
                                paused_rules[rule_id] = datetime.utcnow() + timedelta(seconds=randint(60, 600))
                                record_counter('rule.judge.exceptions.LocksDetected')
                                logging.warning('rule_cleaner[%s/%s]: Locks detected for %s' % (process*threads_per_process+thread, total_processes*threads_per_process-1, rule_id))
                            else:
                                logging.error(traceback.format_exc())
                                record_counter('rule.judge.exceptions.%s' % e.__class__.__name__)
                        else:
                            logging.error(traceback.format_exc())
                            record_counter('rule.judge.exceptions.%s' % e.__class__.__name__)
                record_gauge('rule.judge.cleaner.threads.%d' % (process*threads_per_process+thread), 0)
        except Exception, e:
            record_counter('rule.judge.exceptions.%s' % e.__class__.__name__)
            record_gauge('rule.judge.cleaner.threads.%d' % (process*threads_per_process+thread), 0)
            logging.critical(traceback.format_exc())
        if once:
            return

    logging.info('rule_cleaner: graceful stop requested')
    record_gauge('rule.judge.cleaner.threads.%d' % (process*threads_per_process+thread), 0)
    logging.info('rule_cleaner: graceful stop done')


def stop(signum=None, frame=None):
    """
    Graceful exit.
    """

    graceful_stop.set()


def run(once=False, process=0, total_processes=1, threads_per_process=1):
    """
    Starts up the Judge-Clean threads.
    """

    try:
        ntpc = ntplib.NTPClient()
        response = ntpc.request('137.138.16.69', version=3)  # 137.138.16.69 CERN IP-TIME-1 NTP Server (Stratum 2)
        if response.offset > 60*60+10:  # 1hour 10seconds
            logging.critical('Offset between NTP server and system time too big. Stopping Cleaner')
            return
    except:
        return

    for i in xrange(process * threads_per_process, max(0, process * threads_per_process + threads_per_process - 1)):
        record_gauge('rule.judge.cleaner.threads.%d' % i, 0)

    if once:
        logging.info('main: executing one iteration only')
        rule_cleaner(once)
    else:
        logging.info('main: starting threads')
        threads = [threading.Thread(target=rule_cleaner, kwargs={'process': process, 'total_processes': total_processes, 'once': once, 'thread': i, 'threads_per_process': threads_per_process}) for i in xrange(0, threads_per_process)]
        [t.start() for t in threads]
        logging.info('main: waiting for interrupts')
        # Interruptible joins require a timeout.
        while threads[0].is_alive():
            [t.join(timeout=3.14) for t in threads]
