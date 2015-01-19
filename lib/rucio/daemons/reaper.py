# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2012-2015
# - Cedric Serfon, <cedric.serfon@cern.ch>, 2013-2014
# - Mario Lassnig, <mario.lassnig@cern.ch>, 2014
# - Wen Guan, <wen.guan@cern.ch>, 2014

'''
Reaper is a daemon to manage file deletion.
'''

import logging
import math
import sys
import threading
import time
import traceback

from rucio.core import monitor
from rucio.core import rse as rse_core
from rucio.core.message import add_message
from rucio.core.replica import list_unlocked_replicas, update_replicas_states, delete_replicas
from rucio.core.rse_counter import get_counter
from rucio.core.rse_expression_parser import parse_expression
from rucio.db.constants import ReplicaState
from rucio.rse import rsemanager as rsemgr
from rucio.common.config import config_get
from rucio.common.exception import SourceNotFound, ServiceUnavailable, RSEAccessDenied, ReplicaUnAvailable
from rucio.common.utils import chunks


logging.getLogger("requests").setLevel(logging.CRITICAL)

logging.basicConfig(stream=sys.stdout,
                    level=getattr(logging, config_get('common', 'loglevel').upper()),
                    format='%(asctime)s\t%(process)d\t%(levelname)s\t%(message)s')

graceful_stop = threading.Event()


def __check_rse_usage(rse, rse_id):
    """
    Internal method to check RSE usage and limits.

    :param rse_id: the rse name.
    :param rse_id: the rse id.

    :returns : max_being_deleted_files, needed_free_space, used, free.
    """
    max_being_deleted_files, needed_free_space, used, free = None, None, None, None

    # Get RSE limits
    limits = rse_core.get_rse_limits(rse=rse, rse_id=rse_id)
    if not limits and 'MinFreeSpace' not in limits and 'MaxBeingDeletedFiles' not in limits:
        return max_being_deleted_files, needed_free_space, used, free

    min_free_space = limits.get('MinFreeSpace')
    max_being_deleted_files = limits.get('MaxBeingDeletedFiles')

    # Get total space available
    usage = rse_core.get_rse_usage(rse=rse, rse_id=rse_id, source='srm')
    if not usage:
        return max_being_deleted_files, needed_free_space, used, free

    for u in usage:
        total = u['total']
        break

    # Get current used space
    cnt = get_counter(rse_id=rse_id)
    if not cnt:
        return max_being_deleted_files, needed_free_space, used, free
    used = cnt['bytes']

    # Get current amount of bytes and files waiting for deletion
    # being_deleted = rse_core.get_sum_count_being_deleted(rse_id=rse_id)

    free = total - used
    needed_free_space = min_free_space - free

    return max_being_deleted_files, needed_free_space, used, free


def reaper(rses, worker_number=1, child_number=1, total_children=1, chunk_size=100, once=False, greedy=False, scheme=None, exclude_rses=None, delay_seconds=0):
    """
    Main loop to select and delete files.

    :param rses: List of RSEs the reaper should work against. If empty, it considers all RSEs.
    :param worker_number: The worker number.
    :param child_number: The child number.
    :param total_children: The total number of children created per worker.
    :param chunk_size: the size of chunk for deletion.
    :param once: If True, only runs one iteration of the main loop.
    :param greedy: If True, delete right away replicas with tombstone.
    :param scheme: Force the reaper to use a particular protocol, e.g., mock.
    :param exclude_rses: RSE expression to exclude RSEs from the Reaper.
    """
    logging.info('Starting reaper: worker %(worker_number)s, child %(child_number)s' % locals())
    while not graceful_stop.is_set():
        try:
            max_deleting_rate = 0

            for rse in rses:
                deleting_rate = 0
                rse_info = rsemgr.get_rse_info(rse['rse'])
                rse_protocol = rse_core.get_rse_protocols(rse['rse'])

                if not rse_protocol['availability_delete']:
                    logging.info('Reaper %s-%s: RSE %s is not available for deletion' % (worker_number, child_number, rse_info['rse']))
                    continue

                # Temporary hack to force gfal for deletion
                for protocol in rse_info['protocols']:
                    if protocol['impl'] == 'rucio.rse.protocols.srm.Default' or protocol['impl'] == 'rucio.rse.protocols.gsiftp.Default':
                        protocol['impl'] = 'rucio.rse.protocols.gfal.Default'

                logging.info('Reaper %s-%s: Running on RSE %s' % (worker_number, child_number, rse_info['rse']))
                try:
                    needed_free_space, max_being_deleted_files = None, 10000
                    if not greedy:
                        max_being_deleted_files, needed_free_space, used, free = __check_rse_usage(rse=rse['rse'], rse_id=rse['id'])
                        logging.info('Reaper %(worker_number)s-%(child_number)s: Space usage for RSE %(rse)s - max_being_deleted_files: %(max_being_deleted_files)s, needed_free_space: %(needed_free_space)s, used: %(used)s, free: %(free)s' % locals())
                        if needed_free_space <= 0:
                            needed_free_space = 0
                            logging.info('Reaper %s-%s: free space is above minimum limit for %s' % (worker_number, child_number, rse['rse']))

                    s = time.time()
                    with monitor.record_timer_block('reaper.list_unlocked_replicas'):
                        replicas = list_unlocked_replicas(rse=rse['rse'], bytes=needed_free_space, limit=max_being_deleted_files, worker_number=child_number, total_workers=total_children, delay_seconds=delay_seconds)
                    logging.debug('Reaper %s-%s: list_unlocked_replicas %s %s %s' % (worker_number, child_number, rse['rse'], time.time() - s, len(replicas)))

                    if not replicas:
                        logging.info('Reaper %s-%s: nothing to do for %s' % (worker_number, child_number, rse['rse']))
                        continue

                    p = rsemgr.create_protocol(rse_info, 'delete', scheme=None)
                    for files in chunks(replicas, chunk_size):
                        logging.debug('Reaper %s-%s: Running on : %s' % (worker_number, child_number, str(files)))
                        try:
                            s = time.time()
                            update_replicas_states(replicas=[dict(replica.items() + [('state', ReplicaState.BEING_DELETED), ('rse_id', rse['id'])]) for replica in files])

                            for replica in files:
                                try:
                                    replica['pfn'] = str(rsemgr.lfns2pfns(rse_settings=rse_info, lfns=[{'scope': replica['scope'], 'name': replica['name']}, ], operation='delete').values()[0])
                                except ReplicaUnAvailable as e:
                                    err_msg = 'Failed to get pfn UNAVAILABLE replica %s:%s on %s with error %s' % (replica['scope'], replica['name'], rse['rse'], str(e))
                                    logging.warning('Reaper %s-%s: %s' % (worker_number, child_number, err_msg))
                                    replica['pfn'] = None

                                add_message('deletion-planned', {'scope': replica['scope'],
                                                                 'name': replica['name'],
                                                                 'file-size': replica['bytes'],
                                                                 'url': replica['pfn'],
                                                                 'rse': rse_info['rse']})

                            # logging.debug('update_replicas_states %s' % (time.time() - s))
                            monitor.record_counter(counters='reaper.deletion.being_deleted',  delta=len(files))

                            if not scheme:
                                try:
                                    deleted_files = []
                                    p.connect()
                                    for replica in files:
                                        try:
                                            logging.info('Reaper %s-%s: Deletion ATTEMPT of %s:%s as %s on %s' % (worker_number, child_number, replica['scope'], replica['name'], replica['pfn'], rse['rse']))
                                            s = time.time()
                                            if rse['staging_area'] or rse['rse'].endswith("STAGING"):
                                                logging.warning('Reaper %s-%s: Deletion STAGING of %s:%s as %s on %s, will only delete the catalog and not do physical deletion' % (worker_number,
                                                                                                                                                                                    child_number,
                                                                                                                                                                                    replica['scope'],
                                                                                                                                                                                    replica['name'],
                                                                                                                                                                                    replica['pfn'],
                                                                                                                                                                                    rse['rse']))
                                            else:
                                                if replica['pfn']:
                                                    p.delete(replica['pfn'])
                                                else:
                                                    logging.warning('Reaper %s-%s: Deletion UNAVAILABLE of %s:%s as %s on %s' % (worker_number, child_number, replica['scope'], replica['name'], replica['pfn'], rse['rse']))
                                            monitor.record_timer('daemons.reaper.delete.%s.%s' % (p.attributes['scheme'], rse['rse']), (time.time()-s)*1000)
                                            duration = time.time() - s

                                            deleted_files.append({'scope': replica['scope'], 'name': replica['name']})

                                            add_message('deletion-done', {'scope': replica['scope'],
                                                                          'name': replica['name'],
                                                                          'rse': rse_info['rse'],
                                                                          'file-size': replica['bytes'],
                                                                          'url': replica['pfn'],
                                                                          'duration': duration})
                                            logging.info('Reaper %s-%s: Deletion SUCCESS of %s:%s as %s on %s' % (worker_number, child_number, replica['scope'], replica['name'], replica['pfn'], rse['rse']))
                                        except SourceNotFound:
                                            err_msg = 'Reaper %s-%s: Deletion NOTFOUND of %s:%s as %s on %s' % (worker_number, child_number, replica['scope'], replica['name'], replica['pfn'], rse['rse'])
                                            logging.warning(err_msg)
                                            deleted_files.append({'scope': replica['scope'], 'name': replica['name']})
                                            add_message('deletion-failed', {'scope': replica['scope'],
                                                                            'name': replica['name'],
                                                                            'rse': rse_info['rse'],
                                                                            'file-size': replica['bytes'],
                                                                            'url': replica['pfn'],
                                                                            'reason': err_msg})
                                        except (ServiceUnavailable, RSEAccessDenied) as e:
                                            logging.warning('Reaper %s-%s: Deletion NOACCESS of %s:%s as %s on %s: %s' % (worker_number, child_number, replica['scope'], replica['name'], replica['pfn'], rse['rse'], str(e)))
                                            add_message('deletion-failed', {'scope': replica['scope'],
                                                                            'name': replica['name'],
                                                                            'rse': rse_info['rse'],
                                                                            'file-size': replica['bytes'],
                                                                            'url': replica['pfn'],
                                                                            'reason': str(e)})
                                        except Exception as e:
                                            logging.critical('Reaper %s-%s: Deletion CRITICAL of %s:%s as %s on %s: %s' % (worker_number, child_number, replica['scope'], replica['name'], replica['pfn'], rse['rse'], str(traceback.format_exc())))
                                            add_message('deletion-failed', {'scope': replica['scope'],
                                                                            'name': replica['name'],
                                                                            'rse': rse_info['rse'],
                                                                            'file-size': replica['bytes'],
                                                                            'url': replica['pfn'],
                                                                            'reason': str(e)})
                                        except:
                                            logging.critical('Reaper %s-%s: Deletion CRITICAL of %s:%s as %s on %s: %s' % (worker_number, child_number, replica['scope'], replica['name'], replica['pfn'], rse['rse'], str(traceback.format_exc())))
                                except (ServiceUnavailable, RSEAccessDenied) as e:
                                    for replica in files:
                                        logging.warning('Reaper %s-%s: Deletion NOACCESS of %s:%s as %s on %s: %s' % (worker_number, child_number, replica['scope'], replica['name'], replica['pfn'], rse['rse'], str(e)))
                                        add_message('deletion-failed', {'scope': replica['scope'],
                                                                        'name': replica['name'],
                                                                        'rse': rse_info['rse'],
                                                                        'file-size': replica['bytes'],
                                                                        'url': replica['pfn'],
                                                                        'reason': str(e)})
                                finally:
                                    p.close()
                            s = time.time()
                            with monitor.record_timer_block('reaper.delete_replicas'):
                                delete_replicas(rse=rse['rse'], files=deleted_files)
                            logging.debug('Reaper %s-%s: delete_replicas successes %s %s %s' % (worker_number, child_number, rse['rse'], len(deleted_files), time.time() - s))
                            monitor.record_counter(counters='reaper.deletion.done',  delta=len(deleted_files))
                            deleting_rate += len(deleted_files)
                        except:
                            logging.critical(traceback.format_exc())
                    deleting_rate = deleting_rate * 1.0 / max_being_deleted_files
                    if deleting_rate > max_deleting_rate:
                        max_deleting_rate = deleting_rate
                except:
                    logging.critical(traceback.format_exc())

            if once:
                break

            logging.info(" Reaper %s-%s: max_deleting_rate: %s " % (worker_number, child_number, max_deleting_rate))
            sleep_time = int((1 - max_deleting_rate) * 60 + 1)
            time.sleep(sleep_time)

        except:
            logging.critical(traceback.format_exc())

    logging.info('Graceful stop requested')
    logging.info('Graceful stop done')


def stop(signum=None, frame=None):
    """
    Graceful exit.
    """
    graceful_stop.set()


def run(total_workers=1, chunk_size=100, threads_per_worker=None, once=False, greedy=False, rses=[], scheme=None, exclude_rses=None, include_rses=None, delay_seconds=0):
    """
    Starts up the reaper threads.

    :param total_workers: The total number of workers.
    :param chunk_size: the size of chunk for deletion.
    :param threads_per_worker: Total number of threads created by each worker.
    :param once: If True, only runs one iteration of the main loop.
    :param greedy: If True, delete right away replicas with tombstone.
    :param rses: List of RSEs the reaper should work against. If empty, it considers all RSEs.
    :param scheme: Force the reaper to use a particular protocol/scheme, e.g., mock.
    :param exclude_rses: RSE expression to exclude RSEs from the Reaper.
    :param include_rses: RSE expression to include RSEs.
    """
    logging.info('main: starting processes')

    rses_list = rse_core.list_rses()
    if rses:
        rses = [rse for rse in rses_list if rse['rse'] in rses]
    else:
        rses = rses_list

    if exclude_rses:
        excluded_rses = parse_expression(exclude_rses)
        rses = [rse for rse in rses if rse not in excluded_rses]

    if include_rses:
        included_rses = parse_expression(include_rses)
        rses = [rse for rse in rses if rse in included_rses]

    logging.info('Reaper: This instance will work on RSEs: ' + ', '.join([rse['rse'] for rse in rses]))

    threads = []
    nb_rses_per_worker = int(math.ceil(len(rses) / float(total_workers))) or 1.0
    for worker in xrange(total_workers):
        for child in xrange(threads_per_worker or 1):
            kwargs = {'worker_number': worker,
                      'child_number': child + 1,
                      'total_children': threads_per_worker or 1,
                      'once': once,
                      'chunk_size': chunk_size,
                      'greedy': greedy,
                      'rses': rses[worker * nb_rses_per_worker: worker * nb_rses_per_worker + nb_rses_per_worker],
                      'delay_seconds': delay_seconds,
                      'scheme': scheme}
            threads.append(threading.Thread(target=reaper, kwargs=kwargs))
    [t.start() for t in threads]
    while threads[0].is_alive():
        [t.join(timeout=3.14) for t in threads]
