# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Mario Lassnig, <mario.lassnig@cern.ch>, 2014-2015
# - Cedric Serfon, <cedric.serfon@cern.ch>, 2014
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2014
# - Wen Guan, <wen.guan@cern.ch>, 2014
# - Martin Barisits, <martin.barisits@cern.ch>, 2014

"""
Methods common to different conveyor daemons.
"""

import datetime
import json
import logging
import sys
import time
import traceback

from rucio.common import exception
from rucio.common.config import config_get
from rucio.common.exception import UnsupportedOperation
from rucio.core import did, lock, replica, request, rse as rse_core
from rucio.core.message import add_message
from rucio.core.monitor import record_timer
from rucio.db.constants import DIDType, RequestState, ReplicaState, RequestType
from rucio.db.session import transactional_session


@transactional_session
def update_requests_states(reponses, session=None):
    """
    Bulk version used by poller and consumer to update the internal state of requests,
    after the response by the external transfertool.

    :param reqs: List of (req, response) tuples.
    :param session: The database session to use.
    """

    for response in reponses:
        update_request_state(response=response, session=session)


@transactional_session
def update_request_state(response, session=None):
    """
    Used by poller and consumer to update the internal state of requests,
    after the response by the external transfertool.

    :param response: The transfertool response dictionary, retrieved via request.query_request().
    :param session: The database session to use.
    :returns commit_or_rollback: Boolean.
    """

    try:
        request.touch_request(response['request_id'], session=session)
    except exception.UnsupportedOperation, e:
        logging.warning("Request %s doesn't exist anymore, should not be updated again. Error: %s" % (response['request_id'], str(e).replace('\n', '')))
        return False

    if not response['new_state']:
        return False
    elif response['new_state'] == RequestState.LOST:
        logging.debug('UPDATING REQUEST %s FOR STATE %s' % (str(response['request_id']), str(response['new_state'])))
    elif response['new_state'] and 'job_state' in response and response['job_state']:
        logging.debug('UPDATING REQUEST %s FOR TRANSFER(%s) STATE %s' % (str(response['request_id']), str(response['transfer_id']), str(response['job_state'])))
    else:
        return False

    if response['new_state']:

        request.set_request_state(response['request_id'],
                                  response['new_state'],
                                  session=session)

        if response['new_state'] == RequestState.DONE:
            rse_name = response['dst_rse']
            rse_update_name = rse_name

            req = request.get_request(response['request_id'], session=session)
            if req['request_type'] == RequestType.STAGEIN:
                rse_update_name = rse_core.list_rse_attributes(response['dst_rse'], session=session)['staging_buffer']
                logging.debug('OVERRIDE REPLICA DID %s:%s RSE %s TO %s' % (response['scope'], response['name'], response['dst_rse'], rse_update_name))

            try:
                tss = time.time()
                logging.debug('UPDATE REPLICA STATE DID %s:%s RSE %s' % (response['scope'], response['name'], rse_update_name))

                # make sure we do not leave the transaction
                try:
                    # try quickly
                    replica.update_replicas_states([{'rse': rse_update_name,
                                                     'scope': response['scope'],
                                                     'name': response['name'],
                                                     'state': ReplicaState.AVAILABLE}],
                                                   nowait=False,
                                                   session=session)
                except UnsupportedOperation:
                    # replica not found, but it has been transferred because cancel came too late.
                    # so we need to register the replica and schedule it for deletion again
                    record_timer('daemons.conveyor.common.update_request_state.replica-update_replicas_states', (time.time()-tss)*1000)
                    logging.warn('DID %s:%s AT RSE %s NOT FOUND - Registering replica and scheduling for immediate deletion' % (response['scope'],
                                                                                                                                response['name'],
                                                                                                                                rse_name))
                    did_meta = None
                    try:
                        did_meta = did.get_metadata(response['scope'],
                                                    response['name'],
                                                    session=session)
                    except:
                        logging.critical('DID %s:%s NOT FOUND - Cannot re-register replica - potential dark data' % (response['scope'],
                                                                                                                     response['name']))
                        raise

                    if did_meta:
                        try:
                            replica.add_replica(rse_name,
                                                response['scope'],
                                                response['name'],
                                                did_meta['bytes'],
                                                did_meta['account'],
                                                adler32=did_meta['adler32'],
                                                tombstone=datetime.datetime.utcnow(),
                                                session=session)
                        except:
                            logging.critical('Cannot register replica for DID %s:%s at RSE %s - potential dark data' % (response['scope'],
                                                                                                                        response['name'],
                                                                                                                        rse_name))
                            raise

                except:
                    # could not update successful lock
                    record_timer('daemons.conveyor.common.update_request_state.replica-update_replicas_states', (time.time()-tss)*1000)
                    logging.warn("Could not update replica state for successful transfer %s:%s at %s: %s" % (response['scope'],
                                                                                                             response['name'],
                                                                                                             rse_name,
                                                                                                             traceback.format_exc()))
                    raise

                record_timer('daemons.conveyor.common.update_request_state.replica-update_replicas_states', (time.time()-tss)*1000)

                tss = time.time()
                request.archive_request(response['request_id'], session=session)
                record_timer('daemons.conveyor.common.update_request_state.request-archive_request', (time.time()-tss)*1000)

                add_monitor_message(response, session=session)
            except exception.UnsupportedOperation, e:
                # The replica doesn't exist
                request.archive_request(response['request_id'], session=session)
                logging.warning(str(e).replace('\n', ''))
                return True
            except:
                logging.critical("Something unexpected happened when updating replica state for successful transfer %s:%s at %s (%s)" % (response['scope'],
                                                                                                                                         response['name'],
                                                                                                                                         rse_name,
                                                                                                                                         traceback.format_exc()))
                raise

        elif response['new_state'] == RequestState.FAILED:

            rse_name = response['dst_rse']
            rse_update_name = rse_name

            req = request.get_request(response['request_id'], session=session)
            if req['request_type'] == RequestType.STAGEIN:
                rse_update_name = rse_core.list_rse_attributes(response['dst_rse'], session=session)['staging_buffer']
                logging.debug('OVERRIDE REPLICA DID %s:%s RSE %s TO %s' % (response['scope'], response['name'], response['dst_rse'], rse_update_name))

            tss = time.time()
            new_req = request.requeue_and_archive(response['request_id'], session=session)
            record_timer('daemons.conveyor.common.update_request_state.request-requeue_and_archive', (time.time()-tss)*1000)

            add_monitor_message(response, session=session)

            tss = time.time()
            if new_req is None:
                logging.warn('EXCEEDED DID %s:%s REQUEST %s' % (response['scope'],
                                                                response['name'],
                                                                response['request_id']))
                try:
                    replica.update_replicas_states([{'rse': rse_update_name,
                                                     'scope': response['scope'],
                                                     'name': response['name'],
                                                     'state': ReplicaState.UNAVAILABLE}],
                                                   session=session)
                except:
                    logging.critical("Could not update replica state for failed transfer %s:%s at %s (%s)" % (response['scope'],
                                                                                                              response['name'],
                                                                                                              rse_update_name,
                                                                                                              traceback.format_exc()))
                    raise

                tss = time.time()
                try:
                    lock.failed_transfer(response['scope'],
                                         response['name'],
                                         rse_core.get_rse_id(rse=rse_update_name, session=session),
                                         session=session)
                except:
                    logging.warn('Could not update lock for failed transfer %s:%s at %s (%s)' % (response['scope'],
                                                                                                 response['name'],
                                                                                                 rse_update_name,
                                                                                                 traceback.format_exc()))
                    raise

                record_timer('daemons.conveyor.common.update_request_state.lock-failed_transfer', (time.time()-tss)*1000)
            else:
                logging.warn('REQUEUED DID %s:%s REQUEST %s AS %s TRY %s' % (response['scope'],
                                                                             response['name'],
                                                                             response['request_id'],
                                                                             new_req['request_id'],
                                                                             new_req['retry_count']))

        elif response['new_state'] == RequestState.LOST:
            req = request.get_request(response['request_id'])
            rse_name = rse_core.get_rse_name(rse_id=req['dest_rse_id'], session=session)
            rse_update_name = rse_name

            if req['request_type'] == RequestType.STAGEIN:
                rse_update_name = rse_core.list_rse_attributes(response['dst_rse'], session=session)['staging_buffer']
                logging.debug('OVERRIDE REPLICA DID %s:%s RSE %s TO %s' % (response['scope'], response['name'], response['dst_rse'], rse_update_name))

            response['scope'] = req['scope']
            response['name'] = req['name']
            response['dest_rse_id'] = rse_core.get_rse_id(rse=rse_update_name, session=session)
            response['dst_rse'] = rse_name

            add_monitor_message(response, session=session)

            request.archive_request(response['request_id'], session=session)
            logging.error('LOST DID %s:%s REQUEST %s' % (response['scope'],
                                                         response['name'],
                                                         response['request_id']))

            try:
                lock.failed_transfer(response['scope'],
                                     response['name'],
                                     response['dest_rse_id'],
                                     session=session)
            except:
                logging.warn('Could not update lock for lost transfer %s:%s at %s (%s)' % (response['scope'],
                                                                                           response['name'],
                                                                                           rse_update_name,
                                                                                           sys.exc_info()[1]))
                raise

        logging.info('UPDATED REQUEST %s DID %s:%s AT %s TO %s' % (response['request_id'],
                                                                   response['scope'],
                                                                   response['name'],
                                                                   rse_name,
                                                                   response['new_state']))

    return True


def get_source_rse(scope, name, src_url):
    try:
        scheme = src_url.split(":")[0]
        replications = replica.list_replicas([{'scope': scope, 'name': name, 'type': DIDType.FILE}], schemes=[scheme], unavailable=True)
        for source in replications:
            for source_rse in source['rses']:
                for pfn in source['rses'][source_rse]:
                    if pfn == src_url:
                        return source_rse
        # cannot find matched surl
        logging.warn('Cannot get correct RSE for source url: %s' % (src_url))
        return None
    except:
        logging.error('Cannot get correct RSE for source url: %s(%s)' % (src_url, sys.exc_info()[1]))
        return None


@transactional_session
def add_monitor_message(response, session=None):
    if response['new_state'] == RequestState.DONE:
        transfer_status = 'transfer-done'
    elif response['new_state'] == RequestState.FAILED:
        transfer_status = 'transfer-failed'
    elif response['new_state'] == RequestState.LOST:
        transfer_status = 'transfer-lost'

    activity = response.get('activity', None)
    src_rse = response.get('src_rse', None)
    src_url = response.get('src_url', None)
    dst_rse = response.get('dst_rse', None)
    dst_url = response.get('dst_url', None)
    dst_protocol = dst_url.split(':')[0] if dst_url else None
    reason = response.get('reason', None)
    duration = response.get('duration', -1)
    filesize = response.get('filesize', None)
    md5 = response.get('md5', None)
    adler32 = response.get('adler32', None)
    scope = response.get('scope', None)
    name = response.get('name', None)
    job_m_replica = response.get('job_m_replica', None)
    if job_m_replica and str(job_m_replica) == str('true'):
        try:
            rse_name = get_source_rse(scope, name, src_url)
        except:
            logging.warn('Cannot get correct RSE for source url: %s(%s)' % (src_url, sys.exc_info()[1]))
            rse_name = None
        if rse_name and rse_name != src_rse:
            src_rse = rse_name
            logging.info('find RSE: %s for source surl: %s' % (src_rse, src_url))

    add_message(transfer_status, {'activity': activity,
                                  'request-id': response['request_id'],
                                  'duration': duration,
                                  'checksum-adler': adler32,
                                  'checksum-md5': md5,
                                  'file-size': filesize,
                                  'guid': None,
                                  'previous-request-id': response['previous_attempt_id'],
                                  'protocol': dst_protocol,
                                  'scope': response['scope'],
                                  'name': response['name'],
                                  'src-rse': src_rse,
                                  'src-url': src_url,
                                  'dst-rse': dst_rse,
                                  'dst-url': dst_url,
                                  'reason': reason,
                                  'transfer-endpoint': response['external_host'],
                                  'transfer-id': response['transfer_id'],
                                  'transfer-link': 'https://%s:8449/fts3/ftsmon/#/job/%s' % (response['external_host'],
                                                                                             response['transfer_id']),
                                  'tool-id': 'rucio-conveyor'},
                session=session)


@transactional_session
def update_bad_request(req, dest_rse, new_state, detail, session=None):
    if new_state == RequestState.FAILED:
        request.set_request_state(req['request_id'], new_state, session=session)

        activity = 'default'
        if req['attributes']:
            if type(req['attributes']) is dict:
                req_attributes = json.loads(json.dumps(req['attributes']))
            else:
                req_attributes = json.loads(str(req['attributes']))
            activity = req_attributes['activity'] if req_attributes['activity'] else 'default'

        tss = time.time()
        add_message('transfer-failed', {'activity': activity,
                                        'request-id': req['request_id'],
                                        'checksum-adler': None,
                                        'checksum-md5': None,
                                        'dst-rse': dest_rse,
                                        'dst-url': None,
                                        'name': req['name'],
                                        'guid': None,
                                        'file-size': None,
                                        'previous-request-id': req['request_id'],
                                        'protocol': None,
                                        'reason': detail,
                                        'transfer-link': None,
                                        'scope': req['scope'],
                                        'src-rse': None,
                                        'src-url': None,
                                        'tool-id': 'rucio-conveyor',
                                        'transfer-endpoint': config_get('conveyor', 'ftshosts'),
                                        'transfer-id': None},
                    session=session)

        request.archive_request(req['request_id'], session=session)
        logging.error('BAD DID %s:%s REQUEST %s details: %s' % (req['scope'],
                                                                req['name'],
                                                                req['request_id'],
                                                                detail))
        try:
            replica.update_replicas_states([{'rse': dest_rse,
                                             'scope': req['scope'],
                                             'name': req['name'],
                                             'state': ReplicaState.UNAVAILABLE}],
                                           session=session)
        except:
            logging.critical("Could not update replica state for failed transfer %s:%s at %s (%s)" % (req['scope'],
                                                                                                      req['name'],
                                                                                                      dest_rse,
                                                                                                      traceback.format_exc()))
            raise

        tss = time.time()
        try:
            lock.failed_transfer(req['scope'],
                                 req['name'],
                                 req['dest_rse_id'],
                                 session=session)
        except:
            logging.warn('Could not update lock for failed transfer %s:%s at %s (%s)' % (req['scope'],
                                                                                         req['name'],
                                                                                         dest_rse,
                                                                                         traceback.format_exc()))
            raise
        record_timer('daemons.conveyor.common.update_request_state.lock-failed_transfer', (time.time()-tss)*1000)
