# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Martin Barisits, <martin.barisits@cern.ch>, 2014-2015
# - Mario Lassnig, <mario.lassnig@cern.ch>, 2014

from rucio.common.utils import generate_uuid as uuid
from rucio.core.account_counter import get_counter
from rucio.core.did import add_did, attach_dids, detach_dids
from rucio.core.lock import get_replica_locks, get_dataset_locks
from rucio.core.rse import add_rse_attribute, get_rse
from rucio.core.rule import add_rule
from rucio.daemons.judge.evaluator import re_evaluator
from rucio.daemons.abacus.account import account_update
from rucio.db.constants import DIDType
from rucio.tests.test_rule import create_files, tag_generator


class TestJudgeEvaluator():

    @classmethod
    def setUpClass(cls):
        # Add test RSE
        cls.rse1 = 'MOCK'
        cls.rse3 = 'MOCK3'
        cls.rse4 = 'MOCK4'
        cls.rse5 = 'MOCK5'

        cls.rse1_id = get_rse(cls.rse1).id
        cls.rse3_id = get_rse(cls.rse3).id
        cls.rse4_id = get_rse(cls.rse4).id
        cls.rse5_id = get_rse(cls.rse5).id

        # Add Tags
        cls.T1 = tag_generator()
        cls.T2 = tag_generator()
        add_rse_attribute(cls.rse1, cls.T1, True)
        add_rse_attribute(cls.rse3, cls.T1, True)
        add_rse_attribute(cls.rse4, cls.T2, True)
        add_rse_attribute(cls.rse5, cls.T1, True)

        # Add fake weights
        add_rse_attribute(cls.rse1, "fakeweight", 10)
        add_rse_attribute(cls.rse3, "fakeweight", 0)
        add_rse_attribute(cls.rse4, "fakeweight", 0)
        add_rse_attribute(cls.rse5, "fakeweight", 0)

    def test_judge_add_files_to_dataset(self):
        """ JUDGE EVALUATOR: Test the judge when adding files to dataset"""
        scope = 'mock'
        files = create_files(3, scope, self.rse1)
        dataset = 'dataset_' + str(uuid())
        add_did(scope, dataset, DIDType.from_sym('DATASET'), 'jdoe')

        # Add a first rule to the DS
        add_rule(dids=[{'scope': scope, 'name': dataset}], account='jdoe', copies=2, rse_expression=self.T1, grouping='DATASET', weight=None, lifetime=None, locked=False, subscription_id=None)

        attach_dids(scope, dataset, files, 'jdoe')
        re_evaluator(once=True)

        files = create_files(3, scope, self.rse1)
        attach_dids(scope, dataset, files, 'jdoe')

        # Fake judge
        re_evaluator(once=True)

        # Check if the Locks are created properly
        for file in files:
            assert(len(get_replica_locks(scope=file['scope'], name=file['name'])) == 2)

    def test_judge_add_dataset_to_container(self):
        """ JUDGE EVALUATOR: Test the judge when adding dataset to container"""
        scope = 'mock'
        files = create_files(3, scope, self.rse1)
        dataset = 'dataset_' + str(uuid())
        add_did(scope, dataset, DIDType.from_sym('DATASET'), 'jdoe')
        attach_dids(scope, dataset, files, 'jdoe')

        parent_container = 'dataset_' + str(uuid())
        add_did(scope, parent_container, DIDType.from_sym('CONTAINER'), 'jdoe')
        # Add a first rule to the DS
        add_rule(dids=[{'scope': scope, 'name': parent_container}], account='jdoe', copies=2, rse_expression=self.T1, grouping='DATASET', weight=None, lifetime=None, locked=False, subscription_id=None)
        attach_dids(scope, parent_container, [{'scope': scope, 'name': dataset}], 'jdoe')
        # Fake judge
        re_evaluator(once=True)

        # Check if the Locks are created properly
        for file in files:
            assert(len(get_replica_locks(scope=file['scope'], name=file['name'])) == 2)

        # Check if the DatasetLocks are created properly
        dataset_locks = [lock for lock in get_dataset_locks(scope=scope, name=dataset)]
        assert(len(dataset_locks) == 2)

    def test_account_counter_judge_evaluate_attach(self):
        """ JUDGE EVALUATOR: Test if the account counter is updated correctly when a file is added to a DS"""
        re_evaluator(once=True)
        account_update(once=True)

        scope = 'mock'
        files = create_files(3, scope, self.rse1, bytes=100)
        dataset = 'dataset_' + str(uuid())
        add_did(scope, dataset, DIDType.from_sym('DATASET'), 'jdoe')

        # Add a first rule to the DS
        add_rule(dids=[{'scope': scope, 'name': dataset}], account='jdoe', copies=1, rse_expression=self.rse1, grouping='ALL', weight=None, lifetime=None, locked=False, subscription_id=None)

        account_counter_before = get_counter(self.rse1_id, 'jdoe')
        attach_dids(scope, dataset, files, 'jdoe')

        # Fake judge
        re_evaluator(once=True)
        account_update(once=True)

        account_counter_after = get_counter(self.rse1_id, 'jdoe')
        assert(account_counter_before['bytes'] + 3*100 == account_counter_after['bytes'])
        assert(account_counter_before['files'] + 3 == account_counter_after['files'])

    def test_account_counter_judge_evaluate_detach(self):
        """ JUDGE EVALUATOR: Test if the account counter is updated correctly when a file is removed from a DS"""
        re_evaluator(once=True)
        account_update(once=True)

        scope = 'mock'
        files = create_files(3, scope, self.rse1, bytes=100)
        dataset = 'dataset_' + str(uuid())
        add_did(scope, dataset, DIDType.from_sym('DATASET'), 'jdoe')
        attach_dids(scope, dataset, files, 'jdoe')

        # Add a first rule to the DS
        add_rule(dids=[{'scope': scope, 'name': dataset}], account='jdoe', copies=1, rse_expression=self.rse1, grouping='ALL', weight=None, lifetime=None, locked=False, subscription_id=None)

        account_update(once=True)

        account_counter_before = get_counter(self.rse1_id, 'jdoe')

        detach_dids(scope, dataset, [files[0]])

        # Fake judge
        re_evaluator(once=True)
        account_update(once=True)

        account_counter_after = get_counter(self.rse1_id, 'jdoe')
        assert(account_counter_before['bytes'] - 100 == account_counter_after['bytes'])
        assert(account_counter_before['files'] - 1 == account_counter_after['files'])

    def test_judge_evaluate_detach_datasetlock(self):
        """ JUDGE EVALUATOR: Test if the a datasetlock is detached correctly when removing a dataset from a container"""
        re_evaluator(once=True)

        scope = 'mock'
        files = create_files(3, scope, self.rse1, bytes=100)
        dataset = 'dataset_' + str(uuid())
        add_did(scope, dataset, DIDType.from_sym('DATASET'), 'jdoe')
        attach_dids(scope, dataset, files, 'jdoe')

        container = 'container_' + str(uuid())
        add_did(scope, container, DIDType.from_sym('CONTAINER'), 'jdoe')
        attach_dids(scope, container, [{'scope': scope, 'name': dataset}], 'jdoe')

        # Add a rule to the Container
        add_rule(dids=[{'scope': scope, 'name': container}], account='jdoe', copies=1, rse_expression=self.rse1, grouping='DATASET', weight=None, lifetime=None, locked=False, subscription_id=None)

        # Check if the datasetlock is there
        locks = [ds_lock for ds_lock in get_dataset_locks(scope=scope, name=dataset)]
        assert(len(locks) > 0)

        detach_dids(scope, container, [{'scope': scope, 'name': dataset}])

        # Fake judge
        re_evaluator(once=True)

        locks = [ds_lock for ds_lock in get_dataset_locks(scope=scope, name=dataset)]
        assert(len(locks) == 0)
