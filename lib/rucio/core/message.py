# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2013-2014
# - Mario Lassnig, <mario.lassnig@cern.ch>, 2014
# - Martin Barisits, <martin.barisits@cern.ch>, 2014

import json

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import bindparam, text

from rucio.common.exception import InvalidObject, RucioException
from rucio.db.models import Message
from rucio.db.session import transactional_session


@transactional_session
def add_message(event_type, payload, session=None):
    """
    Add a message to be submitted asynchronously to a message broker.

    :param event_type: The type of the event as a string, e.g., NEW_DID.
    :param payload: The message payload. Will be persisted as JSON.
    :param session: The database session to use.
    """

    try:
        new_message = Message(event_type=event_type, payload=json.dumps(payload))
    except TypeError, e:
        raise InvalidObject('Invalid JSON for payload: %(e)s' % locals())

    new_message.save(session=session, flush=False)


@transactional_session
def retrieve_messages(bulk=1000, process=None, total_processes=None, thread=None, total_threads=None, session=None):
    """
    Retrieve up to $bulk messages.

    :param bulk: Number of messages as an integer.
    :param process: Identifier of the caller process as an integer.
    :param total_processes: Maximum number of processes as an integer.
    :param thread: Identifier of the caller thread as an integer.
    :param total_threads: Maximum number of threads as an integer.
    :param session: The database session to use.

    :returns messages: List of dictionaries {id, created_at, event_type, payload}
    """

    messages = []

    try:
        query = session.query(Message.id,
                              Message.created_at,
                              Message.event_type,
                              Message.payload).order_by(Message.created_at)

        if total_processes and (total_processes-1) > 0:
            if session.bind.dialect.name == 'oracle':
                bindparams = [bindparam('process_number', process), bindparam('total_processes', total_processes-1)]
                query = query.filter(text('ORA_HASH(id, :total_processes) = :process_number', bindparams=bindparams))
            elif session.bind.dialect.name == 'mysql':
                query = query.filter('mod(md5(id), %s) = %s' % (total_processes-1, process))
            elif session.bind.dialect.name == 'postgresql':
                query = query.filter('mod(abs((\'x\'||md5(id))::bit(32)::int), %s) = %s' % (total_processes-1, process))

        if total_threads and (total_threads-1) > 0:
            if session.bind.dialect.name == 'oracle':
                bindparams = [bindparam('thread_number', thread), bindparam('total_threads', total_threads-1)]
                query = query.filter(text('ORA_HASH(id, :total_threads) = :thread_number', bindparams=bindparams))
            elif session.bind.dialect.name == 'mysql':
                query = query.filter('mod(md5(id), %s) = %s' % (total_threads-1, thread))
            elif session.bind.dialect.name == 'postgresql':
                query = query.filter('mod(abs((\'x\'||md5(id))::bit(32)::int), %s) = %s' % (total_threads-1, thread))

        query = query.limit(bulk)

        for id, created_at, event_type, payload in query:
            messages.append({'id': id,
                             'created_at': created_at,
                             'event_type': event_type,
                             'payload': json.loads(str(payload))})
        return messages

    except IntegrityError, e:
        raise RucioException(e.args)


@transactional_session
def delete_messages(ids, session=None):
    """
    Delete all messages with the given IDs.

    :param ids: The message IDs, as a list of strings.
    """

    try:
        for id in ids:
            session.query(Message).\
                filter_by(id=id).\
                delete(synchronize_session=False)
    except IntegrityError, e:
        raise RucioException(e.args)


@transactional_session
def truncate_messages(session=None):
    """
    Delete all stored messages. This is for internal purposes only.

    :param session: The database session to use.
    """

    try:
        session.query(Message).delete(synchronize_session=False)
    except IntegrityError, e:
        raise RucioException(e.args)
