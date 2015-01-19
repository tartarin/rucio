# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Cedric Serfon, <cedric.serfon@cern.ch>, 2013
# - Thomas Beermann, <thomas.beermann@cern.ch>, 2014

from json import dumps, loads

from nose.tools import assert_equal, assert_true, raises, assert_raises
from paste.fixture import TestApp

from rucio.api.subscription import list_subscriptions, add_subscription, update_subscription, list_subscription_rule_states, get_subscription_by_id
from rucio.client.subscriptionclient import SubscriptionClient
from rucio.common.exception import InvalidObject, SubscriptionNotFound, SubscriptionDuplicate
from rucio.common.utils import generate_uuid as uuid
from rucio.core.did import add_did
from rucio.core.rse import add_rse
from rucio.core.rule import add_rule
from rucio.core.scope import add_scope
from rucio.db.constants import DIDType
from rucio.web.rest.authentication import app as auth_app
from rucio.web.rest.subscription import app as subs_app


class TestSubscriptionCoreApi():

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_create_and_update_and_list_subscription(self):
        """ SUBSCRIPTION (API): Test the creation of a new subscription, update it, list it """
        subscription_name = uuid()
        result = add_subscription(name=subscription_name, account='root', filter={'project': ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'], 'datatype': ['AOD', ], 'excluded_pattern':
                                  '(_tid|physics_(Muons|JetTauEtmiss|Egamma)\..*\.ESD|express_express(?!.*NTUP|.*\.ESD|.*RAW)|(physics|express)(?!.*NTUP).* \
                                  \.x|physics_WarmStart|calibration(?!_PixelBeam.merge.(NTUP_IDVTXLUMI|AOD))|merge.HIST|NTUP_MUONCALIB|NTUP_TRIG)', 'account': 'tier0'},
                                  replication_rules=[(2, 'T1_DATATAPE', True, True), (1, 'T1_DATADISK', False, True)], lifetime=100000, retroactive=0, dry_run=0, comments='This is a comment')
        with assert_raises(TypeError):
            result = update_subscription(name=subscription_name, account='root', filter='toto')
        with assert_raises(InvalidObject):
            result = update_subscription(name=subscription_name, account='root', filter={'project': 'toto'})
        result = update_subscription(name=subscription_name, account='root', filter={'project': ['toto', ]})
        assert_equal(result, None)
        result = list_subscriptions(name=subscription_name, account='root')
        sub = []
        for r in result:
            sub.append(r)
        assert_equal(len(sub), 1)
        assert_equal(loads(sub[0]['filter'])['project'][0], 'toto')

    def test_create_list_subscription_by_id(self):
        """ SUBSCRIPTION (API): Test the creation of a new subscription and list it by id """
        subscription_name = uuid()
        subscription_id = add_subscription(name=subscription_name, account='root', filter={'project': ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'], 'datatype': ['AOD', ], 'excluded_pattern':
                                                                                           '(_tid|physics_(Muons|JetTauEtmiss|Egamma)\..*\.ESD|express_express(?!.*NTUP|.*\.ESD|.*RAW)|(physics|express)(?!.*NTUP).* \
                                                                                           \.x|physics_WarmStart|calibration(?!_PixelBeam.merge.(NTUP_IDVTXLUMI|AOD))|merge.HIST|NTUP_MUONCALIB|NTUP_TRIG)', 'account': 'tier0'},
                                           replication_rules=[(2, 'T1_DATATAPE', True, True), (1, 'T1_DATADISK', False, True)], lifetime=100000, retroactive=0, dry_run=0, comments='This is a comment')
        subscription_info = get_subscription_by_id(subscription_id)
        assert_equal(loads(subscription_info['filter'])['project'], ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'])

    @raises(SubscriptionDuplicate)
    def test_create_existing_subscription(self):
        """ SUBSCRIPTION (API): Test the creation of a existing subscription """
        subscription_name = uuid()
        add_subscription(name=subscription_name, account='root', filter={'project': ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'], 'datatype': ['AOD', ], 'excluded_pattern':
                         '(_tid|physics_(Muons|JetTauEtmiss|Egamma)\..*\.ESD|express_express(?!.*NTUP|.*\.ESD|.*RAW)|(physics|express)(?!.*NTUP).* \
                         \.x|physics_WarmStart|calibration(?!_PixelBeam.merge.(NTUP_IDVTXLUMI|AOD))|merge.HIST|NTUP_MUONCALIB|NTUP_TRIG)', 'account': 'tier0'},
                         replication_rules=[(2, 'T1_DATATAPE', True, True), (1, 'T1_DATADISK', False, True)], lifetime=100000, retroactive=0, dry_run=0, comments='This is a comment')
        add_subscription(name=subscription_name, account='root', filter={'project': ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'], 'datatype': ['AOD', ], 'excluded_pattern':
                         '(_tid|physics_(Muons|JetTauEtmiss|Egamma)\..*\.ESD|express_express(?!.*NTUP|.*\.ESD|.*RAW)|(physics|express)(?!.*NTUP).* \
                         \.x|physics_WarmStart|calibration(?!_PixelBeam.merge.(NTUP_IDVTXLUMI|AOD))|merge.HIST|NTUP_MUONCALIB|NTUP_TRIG)', 'account': 'tier0'},
                         replication_rules=[(2, 'T1_DATATAPE', True, True), (1, 'T1_DATADISK', False, True)], lifetime=100000, retroactive=0, dry_run=0, comments='This is a comment')

    @raises(SubscriptionNotFound)
    def test_update_nonexisting_subscription(self):
        """ SUBSCRIPTION (API): Test the update of a non-existing subscription """
        subscription_name = uuid()
        update_subscription(name=subscription_name, account='root', filter={'project': ['toto', ]})

    def test_list_rules_states(self):
        """ SUBSCRIPTION (API): Test listing of rule states for subscription """
        tmp_scope = 'mock_' + uuid()[:8]
        add_scope(tmp_scope, 'root')
        site_a = 'RSE%s' % uuid().upper()
        site_b = 'RSE%s' % uuid().upper()

        add_rse(site_a)
        add_rse(site_b)

        # add a new dataset
        dsn = 'dataset-%s' % uuid()
        add_did(scope=tmp_scope, name=dsn,
                type=DIDType.DATASET, account='root')

        subscription_name = uuid()
        id = add_subscription(name=subscription_name, account='root', filter={'account': 'root'},
                              replication_rules=[(1, 'T1_DATADISK', False, True)], lifetime=100000, retroactive=0, dry_run=0, comments='This is a comment')

        subscriptions = list_subscriptions(name=subscription_name, account='root')
        # workaround until add_subscription returns the id
        id = None
        for s in subscriptions:
            id = s['id']

        # Add two rules
        add_rule(dids=[{'scope': tmp_scope, 'name': dsn}], account='root', copies=1, rse_expression=site_a, grouping='NONE', weight=None, lifetime=None, locked=False, subscription_id=id)
        add_rule(dids=[{'scope': tmp_scope, 'name': dsn}], account='root', copies=1, rse_expression=site_b, grouping='NONE', weight=None, lifetime=None, locked=False, subscription_id=id)

        for r in list_subscription_rule_states(account='root', name=subscription_name):
            assert_equal(r[3], 2)


class TestSubscriptionRestApi():

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_create_and_update_and_list_subscription(self):
        """ SUBSCRIPTION (REST): Test the creation of a new subscription, update it, list it """
        mw = []

        headers1 = {'X-Rucio-Account': 'root', 'X-Rucio-Username': 'ddmlab', 'X-Rucio-Password': 'secret'}
        r1 = TestApp(auth_app.wsgifunc(*mw)).get('/userpass', headers=headers1, expect_errors=True)

        assert_equal(r1.status, 200)
        token = str(r1.header('X-Rucio-Auth-Token'))

        subscription_name = uuid()
        headers2 = {'X-Rucio-Auth-Token': str(token)}
        data = dumps({'name': subscription_name, 'filter': {'project': ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'], 'datatype': ['AOD', ], 'excluded_pattern':
                     '(_tid|physics_(Muons|JetTauEtmiss|Egamma)\..*\.ESD|express_express(?!.*NTUP|.*\.ESD|.*RAW)|(physics|express)(?!.*NTUP).* \
                     \.x|physics_WarmStart|calibration(?!_PixelBeam.merge.(NTUP_IDVTXLUMI|AOD))|merge.HIST|NTUP_MUONCALIB|NTUP_TRIG)', 'account': 'tier0'},
                      'replication_rules': [(2, 'T1_DATATAPE', True, True), (1, 'T1_DATADISK', False, True)], 'lifetime': 100000, 'retroactive': 0, 'dry_run': 0, 'comments': 'blahblah'})
        r2 = TestApp(subs_app.wsgifunc(*mw)).post('/root/%s' % (subscription_name), headers=headers2, params=data, expect_errors=True)
        assert_equal(r2.status, 201)

        data = dumps({'filter': {'project': ['toto', ]}})
        r3 = TestApp(subs_app.wsgifunc(*mw)).put('/root/%s' % (subscription_name), headers=headers2, params=data, expect_errors=True)
        assert_equal(r3.status, 201)

        r4 = TestApp(subs_app.wsgifunc(*mw)).get('/root/%s' % (subscription_name), headers=headers2, expect_errors=True)
        print r4
        print type(loads(r4.body))
        assert_equal(r4.status, 200)
        assert_equal(loads(loads(r4.body)['filter'])['project'][0], 'toto')

    def test_create_and_list_subscription_by_id(self):
        """ SUBSCRIPTION (REST): Test the creation of a new subscription and get by subscription id """
        mw = []

        headers1 = {'X-Rucio-Account': 'root', 'X-Rucio-Username': 'ddmlab', 'X-Rucio-Password': 'secret'}
        r1 = TestApp(auth_app.wsgifunc(*mw)).get('/userpass', headers=headers1, expect_errors=True)

        assert_equal(r1.status, 200)
        token = str(r1.header('X-Rucio-Auth-Token'))

        subscription_name = uuid()
        headers2 = {'X-Rucio-Auth-Token': str(token)}
        data = dumps({'name': subscription_name, 'filter': {'project': ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'], 'datatype': ['AOD', ], 'excluded_pattern':
                     '(_tid|physics_(Muons|JetTauEtmiss|Egamma)\..*\.ESD|express_express(?!.*NTUP|.*\.ESD|.*RAW)|(physics|express)(?!.*NTUP).* \
                     \.x|physics_WarmStart|calibration(?!_PixelBeam.merge.(NTUP_IDVTXLUMI|AOD))|merge.HIST|NTUP_MUONCALIB|NTUP_TRIG)', 'account': 'tier0'},
                      'replication_rules': [(2, 'T1_DATATAPE', True, True), (1, 'T1_DATADISK', False, True)], 'lifetime': 100000, 'retroactive': 0, 'dry_run': 0, 'comments': 'blahblah'})
        r2 = TestApp(subs_app.wsgifunc(*mw)).post('/root/%s' % (subscription_name), headers=headers2, params=data, expect_errors=True)
        assert_equal(r2.status, 201)

        subscription_id = r2.body
        r3 = TestApp(subs_app.wsgifunc(*mw)).get('/Id/%s' % (subscription_id), headers=headers2, expect_errors=True)
        assert_equal(r3.status, 200)
        assert_equal(loads(loads(r3.body)['filter'])['project'][0], 'data12_900GeV')

    def test_create_existing_subscription(self):
        """ SUBSCRIPTION (REST): Test the creation of a existing subscription """
        mw = []

        headers1 = {'X-Rucio-Account': 'root', 'X-Rucio-Username': 'ddmlab', 'X-Rucio-Password': 'secret'}
        r1 = TestApp(auth_app.wsgifunc(*mw)).get('/userpass', headers=headers1, expect_errors=True)

        assert_equal(r1.status, 200)
        token = str(r1.header('X-Rucio-Auth-Token'))

        subscription_name = uuid()
        headers2 = {'X-Rucio-Auth-Token': str(token)}
        data = dumps({'name': subscription_name, 'filter': {'project': ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'], 'datatype': ['AOD', ], 'excluded_pattern':
                     '(_tid|physics_(Muons|JetTauEtmiss|Egamma)\..*\.ESD|express_express(?!.*NTUP|.*\.ESD|.*RAW)|(physics|express)(?!.*NTUP).*\
                     \.x|physics_WarmStart|calibration(?!_PixelBeam.merge.(NTUP_IDVTXLUMI|AOD))|merge.HIST|NTUP_MUONCALIB|NTUP_TRIG)', 'account': 'tier0'},
                      'replication_rules': [(2, 'T1_DATATAPE', True, True), (1, 'T1_DATADISK', False, True)], 'lifetime': 100000, 'retroactive': 0, 'dry_run': 0, 'comments': 'We are the knights who say Ni !'})
        r2 = TestApp(subs_app.wsgifunc(*mw)).post('/root/' + subscription_name, headers=headers2, params=data, expect_errors=True)
        assert_equal(r2.status, 201)

        r3 = TestApp(subs_app.wsgifunc(*mw)).post('/root/' + subscription_name, headers=headers2, params=data, expect_errors=True)
        assert_equal(r3.header('ExceptionClass'), 'SubscriptionDuplicate')
        assert_equal(r3.status, 409)

    def test_update_nonexisting_subscription(self):
        """ SUBSCRIPTION (REST): Test the update of a non-existing subscription """
        mw = []

        headers1 = {'X-Rucio-Account': 'root', 'X-Rucio-Username': 'ddmlab', 'X-Rucio-Password': 'secret'}
        r1 = TestApp(auth_app.wsgifunc(*mw)).get('/userpass', headers=headers1, expect_errors=True)

        assert_equal(r1.status, 200)
        token = str(r1.header('X-Rucio-Auth-Token'))

        subscription_name = uuid()
        headers2 = {'X-Rucio-Auth-Token': str(token)}

        data = dumps({'name': subscription_name, 'filter': {'project': ['toto', ]}})
        r2 = TestApp(subs_app.wsgifunc(*mw)).put('/root/' + subscription_name, headers=headers2, params=data, expect_errors=True)
        assert_equal(r2.status, 404)
        assert_equal(r2.header('ExceptionClass'), 'SubscriptionNotFound')

    def test_list_rules_states(self):
        """ SUBSCRIPTION (REST): Test listing of rule states for subscription """
        tmp_scope = 'mock_' + uuid()[:8]
        add_scope(tmp_scope, 'root')
        mw = []
        site_a = 'RSE%s' % uuid().upper()
        site_b = 'RSE%s' % uuid().upper()

        add_rse(site_a)
        add_rse(site_b)

        # add a new dataset
        dsn = 'dataset-%s' % uuid()
        add_did(scope=tmp_scope, name=dsn,
                type=DIDType.DATASET, account='root')

        subscription_name = uuid()
        id = add_subscription(name=subscription_name, account='root', filter={'account': 'root'},
                              replication_rules=[(1, 'T1_DATADISK', False, True)], lifetime=100000, retroactive=0, dry_run=0, comments='We want a shrubbery')

        subscriptions = list_subscriptions(name=subscription_name, account='root')

        # workaround until add_subscription returns the id
        id = None
        for s in subscriptions:
            id = s['id']

        # Add two rules
        add_rule(dids=[{'scope': tmp_scope, 'name': dsn}], account='root', copies=1, rse_expression=site_a, grouping='NONE', weight=None, lifetime=None, locked=False, subscription_id=id)
        add_rule(dids=[{'scope': tmp_scope, 'name': dsn}], account='root', copies=1, rse_expression=site_b, grouping='NONE', weight=None, lifetime=None, locked=False, subscription_id=id)

        headers1 = {'X-Rucio-Account': 'root', 'X-Rucio-Username': 'ddmlab', 'X-Rucio-Password': 'secret'}
        r1 = TestApp(auth_app.wsgifunc(*mw)).get('/userpass', headers=headers1, expect_errors=True)

        assert_equal(r1.status, 200)
        token = str(r1.header('X-Rucio-Auth-Token'))

        headers2 = {'X-Rucio-Auth-Token': str(token)}
        r2 = TestApp(subs_app.wsgifunc(*mw)).get('/%s/%s/Rules/States' % ('root', subscription_name), headers=headers2, expect_errors=True)

        for line in r2.body.split('\n'):
            print line
            rs = loads(line)
            if rs[1] == subscription_name:
                break
        assert_equal(rs[3], 2)


class TestSubscriptionClient():

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setup(self):
        self.client = SubscriptionClient()

    def test_create_and_update_and_list_subscription(self):
        """ SUBSCRIPTION (CLIENT): Test the creation of a new subscription, update it, list it """
        subscription_name = uuid()
        subid = self.client.add_subscription(name=subscription_name, account='root', filter={'project': ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'], 'datatype': ['AOD', ], 'excluded_pattern':
                                             '(_tid|physics_(Muons|JetTauEtmiss|Egamma)\..*\.ESD|express_express(?!.*NTUP|.*\.ESD|.*RAW)|(physics|express)(?!.*NTUP).* \
                                             \.x|physics_WarmStart|calibration(?!_PixelBeam.merge.(NTUP_IDVTXLUMI|AOD))|merge.HIST|NTUP_MUONCALIB|NTUP_TRIG)', 'account': 'tier0'},
                                             replication_rules=[(2, 'T1_DATATAPE', True, True), (1, 'T1_DATADISK', False, True)], lifetime=100000, retroactive=0, dry_run=0, comments='Ni ! Ni!')
        result = [sub['id'] for sub in list_subscriptions(name=subscription_name, account='root')]
        assert_equal(subid, result[0])
        with assert_raises(TypeError):
            result = self.client.update_subscription(name=subscription_name, account='root', filter='toto')
        result = self.client.update_subscription(name=subscription_name, account='root', filter={'project': ['toto', ]})
        assert_true(result)
        result = list_subscriptions(name=subscription_name, account='root')
        sub = []
        for r in result:
            sub.append(r)
        assert_equal(len(sub), 1)
        assert_equal(loads(sub[0]['filter'])['project'][0], 'toto')

    @raises(SubscriptionDuplicate)
    def test_create_existing_subscription(self):
        """ SUBSCRIPTION (CLIENT): Test the creation of a existing subscription """
        subscription_name = uuid()
        result = self.client.add_subscription(name=subscription_name, account='root', filter={'project': ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'], 'datatype': ['AOD', ], 'excluded_pattern':
                                              '(_tid|physics_(Muons|JetTauEtmiss|Egamma)\..*\.ESD|express_express(?!.*NTUP|.*\.ESD|.*RAW)|(physics|express)(?!.*NTUP).* \
                                              \.x|physics_WarmStart|calibration(?!_PixelBeam.merge.(NTUP_IDVTXLUMI|AOD))|merge.HIST|NTUP_MUONCALIB|NTUP_TRIG)', 'account': 'tier0'},
                                              replication_rules=[(2, 'T1_DATATAPE', True, True), (1, 'T1_DATADISK', False, True)], lifetime=100000, retroactive=0, dry_run=0, comments='Ni ! Ni!')
        assert_true(result)
        result = self.client.add_subscription(name=subscription_name, account='root', filter={'project': ['data12_900GeV', 'data12_8TeV', 'data13_900GeV', 'data13_8TeV'], 'datatype': ['AOD', ], 'excluded_pattern':
                                              '(_tid|physics_(Muons|JetTauEtmiss|Egamma)\..*\.ESD|express_express(?!.*NTUP|.*\.ESD|.*RAW)|(physics|express)(?!.*NTUP).* \
                                              \.x|physics_WarmStart|calibration(?!_PixelBeam.merge.(NTUP_IDVTXLUMI|AOD))|merge.HIST|NTUP_MUONCALIB|NTUP_TRIG)', 'account': 'tier0'},
                                              replication_rules=[(2, 'T1_DATATAPE', True, True), (1, 'T1_DATADISK', False, True)], lifetime=100000, retroactive=0, dry_run=0, comments='Ni ! Ni!')

    @raises(SubscriptionNotFound)
    def test_update_nonexisting_subscription(self):
        """ SUBSCRIPTION (CLIENT): Test the update of a non-existing subscription """
        subscription_name = uuid()
        self.client.update_subscription(name=subscription_name, filter={'project': ['toto', ]})
