#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2012
# - Martin Barisits, <martin.barisits@cern.ch>, 2013-2015

from logging import getLogger, StreamHandler, DEBUG
from json import dumps, loads
from traceback import format_exc

from web import application, ctx, data, header, Created, InternalError, OK, loadhook

from rucio.api.lock import get_replica_locks_for_rule_id
from rucio.api.rule import add_replication_rule, delete_replication_rule, get_replication_rule, update_replication_rule
from rucio.common.exception import (InsufficientAccountLimit, RuleNotFound, AccessDenied, InvalidRSEExpression,
                                    InvalidReplicationRule, RucioException, DataIdentifierNotFound, InsufficientTargetRSEs,
                                    ReplicationRuleCreationTemporaryFailed, InvalidRuleWeight, StagingAreaRuleRequiresLifetime,
                                    DuplicateRule, InvalidObject)
from rucio.common.utils import generate_http_error, render_json, APIEncoder
from rucio.web.rest.common import rucio_loadhook

logger = getLogger("rucio.rule")
sh = StreamHandler()
sh.setLevel(DEBUG)
logger.addHandler(sh)

urls = ('/(.+)/locks', 'ReplicaLocks',
        '/', 'Rule',
        '/(.+)', 'Rule',)


class Rule:
    """ REST APIs for replication rules. """

    def GET(self, rule_id):
        """ get rule information for given rule id.

        HTTP Success:
            200 OK

        HTTP Error:
            401 Unauthorized
            404 Not Found
            500 InternalError

        :returns: JSON dict containing informations about the requested user.
        """
        header('Content-Type', 'application/json')
        try:
            rule = get_replication_rule(rule_id)
        except RuleNotFound, e:
            raise generate_http_error(404, 'RuleNotFound', e.args[0][0])
        except RucioException, e:
            raise generate_http_error(500, e.__class__.__name__, e.args[0])
        except Exception, e:
            raise InternalError(e)

        return render_json(**rule)

    def PUT(self, rule_id):
        """
        Update the replication rules locked flag .

        HTTP Success:
            200 OK

        HTTP Error:
            401 Unauthorized
            404 Not Found
            500 InternalError
        """
        json_data = data()
        try:
            params = loads(json_data)
            options = params['options']
            update_replication_rule(rule_id=rule_id, options=options, issuer=ctx.env.get('issuer'))
        except AccessDenied, e:
            raise generate_http_error(401, 'AccessDenied', e.args[0][0])
        except RuleNotFound, e:
            raise generate_http_error(404, 'RuleNotFound', e.args[0][0])
        except ValueError:
            raise generate_http_error(400, 'ValueError', 'Cannot decode json parameter list')
        except RucioException, e:
            raise generate_http_error(500, e.__class__.__name__, e.args[0][0])
        raise OK()

    def POST(self):
        """
        Create a new replication rule.

        HTTP Success:
            201 Created

        HTTP Error:
            400 Bad Request
            401 Unauthorized
            404 Not Found
            409 Conflict
            500 Internal Error
        """
        json_data = data()
        try:
            grouping, weight, lifetime, locked, subscription_id, source_replica_expression, activity, notify, purge_replicas, ignore_availability = 'DATASET', None, None, False, None, None, None, None, False, False
            params = loads(json_data)
            dids = params['dids']
            account = params['account']
            copies = params['copies']
            rse_expression = params['rse_expression']
            if 'grouping' in params:
                grouping = params['grouping']
            if 'weight' in params:
                weight = params['weight']
            if 'lifetime' in params:
                lifetime = params['lifetime']
            if 'locked' in params:
                locked = params['locked']
            if 'subscription_id' in params:
                subscription_id = params['subscription_id']
            if 'source_replica_expression' in params:
                source_replica_expression = params['source_replica_expression']
            if 'activity' in params:
                activity = params['activity']
            if 'notify' in params:
                notify = params['notify']
            if 'purge_replicas' in params:
                purge_replicas = params['purge_replicas']
            if 'ignore_availability' in params:
                ignore_availability = params['ignore_availability']
        except ValueError:
            raise generate_http_error(400, 'ValueError', 'Cannot decode json parameter list')

        try:
            rule_ids = add_replication_rule(dids=dids,
                                            copies=copies,
                                            rse_expression=rse_expression,
                                            weight=weight,
                                            lifetime=lifetime,
                                            grouping=grouping,
                                            account=account,
                                            locked=locked,
                                            subscription_id=subscription_id,
                                            source_replica_expression=source_replica_expression,
                                            activity=activity,
                                            notify=notify,
                                            purge_replicas=purge_replicas,
                                            ignore_availability=ignore_availability,
                                            issuer=ctx.env.get('issuer'))
        # TODO: Add all other error cases here
        except InvalidReplicationRule, e:
            raise generate_http_error(409, 'InvalidReplicationRule', e.args[0][0])
        except DuplicateRule, e:
            raise generate_http_error(409, 'DuplicateRule', e.args[0])
        except InsufficientTargetRSEs, e:
            raise generate_http_error(409, 'InsufficientTargetRSEs', e.args[0][0])
        except InsufficientAccountLimit, e:
            raise generate_http_error(409, 'InsufficientAccountLimit', e.args[0][0])
        except InvalidRSEExpression, e:
            raise generate_http_error(409, 'InvalidRSEExpression', e.args[0][0])
        except DataIdentifierNotFound, e:
            raise generate_http_error(404, 'DataIdentifierNotFound', e.args[0][0])
        except ReplicationRuleCreationTemporaryFailed, e:
            raise generate_http_error(409, 'ReplicationRuleCreationTemporaryFailed', e.args[0][0])
        except InvalidRuleWeight, e:
            raise generate_http_error(409, 'InvalidRuleWeight', e.args[0][0])
        except StagingAreaRuleRequiresLifetime, e:
            raise generate_http_error(409, 'StagingAreaRuleRequiresLifetime', e.args[0])
        except InvalidObject, e:
            raise generate_http_error(409, 'InvalidObject', e.args[0])
        except RucioException, e:
            raise generate_http_error(500, e.__class__.__name__, e.args[0][0])
        except Exception, e:
            print e
            print format_exc()
            raise InternalError(e)

        raise Created(dumps(rule_ids))

    def DELETE(self, rule_id):
        """
        Delete a new replication rule.

        HTTP Success:
            200 OK

        HTTP Error:
            401 Unauthorized
            404 Not Found
            500 Internal Error
        """
        try:
            delete_replication_rule(rule_id=rule_id, issuer=ctx.env.get('issuer'))
        except AccessDenied, e:
            raise generate_http_error(401, 'AccessDenied', e.args[0][0])
        except RuleNotFound, e:
            raise generate_http_error(404, 'RuleNotFound', e.args[0][0])
        except Exception, e:
            raise InternalError(e)
        raise OK()


class ReplicaLocks:
    """ REST APIs for replica locks. """

    def GET(self, rule_id):
        """ get locks for a given rule_id.

        HTTP Success:
            200 OK

        HTTP Error:
            404 Not Found
            500 InternalError

        :returns: JSON dict containing informations about the requested user.
        """
        header('Content-Type', 'application/x-json-stream')
        try:
            locks = get_replica_locks_for_rule_id(rule_id)
        except RucioException, e:
            raise generate_http_error(500, e.__class__.__name__, e.args[0])
        except Exception, e:
            raise InternalError(e)

        for lock in locks:
            yield dumps(lock, cls=APIEncoder) + '\n'

"""----------------------
   Web service startup
----------------------"""

app = application(urls, globals())
app.add_processor(loadhook(rucio_loadhook))
application = app.wsgifunc()
