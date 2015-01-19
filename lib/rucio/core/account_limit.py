# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Martin Barisits, <martin.barisits@cern.ch>, 2013-2014

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, or_

from rucio.core.rse import get_rse_name
from rucio.db import models
from rucio.db.session import read_session, transactional_session


@read_session
def get_account_limit(account, rse_id, session=None):
    """
    Returns the account limit for the account on the rse.

    :param account:  Account to check the limit for.
    :param rse_id:   RSE id to check the limit for.
    :param session:  Database session in use.
    :return:         Limit in Bytes.
    """
    try:
        account_limit = session.query(models.AccountLimit).filter(models.AccountLimit.account == account,
                                                                  models.AccountLimit.rse_id == rse_id).one()
        return account_limit.bytes
    except NoResultFound:
        return float("inf")


@read_session
def get_account_limits(account, rse_ids=None, session=None):
    """
    Returns the account limits for the account on the list of rses.

    :param account:  Account to check the limit for.
    :param rse_ids:  List of RSE ids to check the limit for.
    :param session:  Database session in use.
    :return:         Dictionary {'rse_id': bytes, ...}.
    """

    account_limits = {}
    if rse_ids:
        rse_id_clauses = []
        for rse_id in rse_ids:
            rse_id_clauses.append(and_(models.AccountLimit.rse_id == rse_id, models.AccountLimit.account == account))
        rse_id_clause_chunks = [rse_id_clauses[x:x+10] for x in xrange(0, len(rse_id_clauses), 10)]
        for rse_id_chunk in rse_id_clause_chunks:
            tmp_limits = session.query(models.AccountLimit).filter(or_(*rse_id_chunk)).all()
            for limit in tmp_limits:
                account_limits[limit.rse_id] = limit.bytes
    else:
        account_limits_tmp = session.query(models.AccountLimit).filter(models.AccountLimit.account == account).all()
        for limit in account_limits_tmp:
            account_limits[limit.rse_id] = limit.bytes
    return account_limits


@transactional_session
def set_account_limit(account, rse_id, bytes, session=None):
    """
    Returns the limits for the account on the rse.

    :param account:  Account to check the limit for.
    :param rse_id:   RSE id to check the limit for.
    :param bytes:    The limit value, in bytes, to set.
    :param session:  Database session in use.
    """
    try:
        account_limit = session.query(models.AccountLimit).filter(models.AccountLimit.account == account,
                                                                  models.AccountLimit.rse_id == rse_id).one()
        account_limit.bytes = bytes
    except NoResultFound:
        models.AccountLimit(account=account, rse_id=rse_id, bytes=bytes).save(session=session)


@transactional_session
def delete_account_limit(account, rse_id, session=None):
    """
    Deletes an account limit.

    :param account:  Account to delete the limit for.
    :param rse_id:   RSE id to delete the limit for.
    :param session:  Database session in use.
    :returns:        True if something was deleted; False otherwise.
    """
    try:
        session.query(models.AccountLimit).filter(models.AccountLimit.account == account,
                                                  models.AccountLimit.rse_id == rse_id).one().delete(session=session)
        return True
    except NoResultFound:
        return False


@transactional_session
def get_account_usage(account, rse_id=None, session=None):
    """
    Read the account usage and connect it with (if available) the account limits of the account.

    :param account:  The account to read.
    :param rse_id:   The rse_id to read (If none, get all).
    :param session:  Database session in use.

    :returns:        List of dicts {'rse_id', 'bytes_used', 'files_used', 'bytes_limit'}
    """

    if not rse_id:
        # All RSESs
        limits = get_account_limits(account=account, session=session)
        counters = session.query(models.AccountCounter).filter_by(account=account).all()
    else:
        # One RSE
        limits = get_account_limits(account=account, rse_ids=[rse_id], session=session)
        counters = session.query(models.AccountCounter).filter_by(account=account, rse_id=rse_id).all()
    result_list = []
    for counter in counters:
        if counter.bytes > 0 or counter.files > 0 or rse_id in limits.keys():
            result_list.append({'rse': get_rse_name(rse_id=counter.rse_id, session=session),
                                'bytes': counter.bytes, 'files': counter.files,
                                'bytes_limit': limits.get(counter.rse_id, float("Inf")),
                                'bytes_remaining': limits.get(counter.rse_id, float("Inf"))})
    return result_list
