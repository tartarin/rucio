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

from nose.tools import assert_in, assert_is_instance

from rucio.client.dq2client import DQ2Client


class TestDQ2Client:

    def setup(self):
        self.client = DQ2Client()

    def test_finger(self):
        """  Finger (DQ2 CLIENT): """
        ret = self.client.finger()
        assert_is_instance(ret, dict)
        assert_in('nickname', ret)

    def test_bulkDeleteDatasetReplicas(self):
        """  bulkDeleteDatasetReplicas (DQ2 CLIENT): """
        assert(False)

    def test_cancelReplicaDeletions(self):
        """  cancelReplicaDeletions (DQ2 CLIENT): """
        assert(False)

    def test_checkDatasetConsistency(self):
        """  checkDatasetConsistency (DQ2 CLIENT): """
        assert(False)

    def test_closeDataset(self):
        """  closeDataset (DQ2 CLIENT): """
        assert(False)

    def test_declareBadFiles(self):
        """  declareBadFiles (DQ2 CLIENT): """
        assert(False)

    def test_declareSuspiciousFiles(self):
        """  declareSuspiciousFiles (DQ2 CLIENT): """
        assert(False)

    def test_deleteDatasetReplicas(self):
        """  deleteDatasetReplicas (DQ2 CLIENT): """
        assert(False)

    def test_deleteDatasetSubscription(self):
        """  deleteDatasetSubscription (DQ2 CLIENT): """
        assert(False)

    def test_deleteDatasetSubscriptions(self):
        """  deleteDatasetSubscriptions (DQ2 CLIENT): """
        assert(False)

    def test_deleteDatasetVersionSubscriptions(self):
        """  deleteDatasetVersionSubscriptions (DQ2 CLIENT): """
        assert(False)

    def test_deleteDatasetsFromContainer(self):
        """  deleteDatasetsFromContainer (DQ2 CLIENT): """
        assert(False)

    def test_deleteFilesFromDataset(self):
        """  deleteFilesFromDataset (DQ2 CLIENT): """
        assert(False)

    def test_eraseDataset(self):
        """  eraseDataset (DQ2 CLIENT): """
        assert(False)

    def test_freezeDataset(self):
        """  freezeDataset (DQ2 CLIENT): """
        assert(False)

    def test_getDatasetSize(self):
        """  getDatasetSize (DQ2 CLIENT): """
        assert(False)

    def test_getMasterReplicaLocation(self):
        """  getMasterReplicaLocation (DQ2 CLIENT): """
        assert(False)

    def test_getMetaDataAttribute(self):
        """  getMetaDataAttribute (DQ2 CLIENT): """
        assert(False)

    def test_getNumberOfFiles(self):
        """  getNumberOfFiles (DQ2 CLIENT): """
        assert(False)

    def test_getState(self):
        """  getState (DQ2 CLIENT): """
        assert(False)

    def test_getVersionMetadata(self):
        """  getVersionMetadata (DQ2 CLIENT): """
        assert(False)

    def test_listDatasetReplicas(self):
        """  listDatasetReplicas (DQ2 CLIENT): """
        assert(False)

    def test_listDatasetReplicasInContainer(self):
        """  listDatasetReplicasInContainer (DQ2 CLIENT): """
        assert(False)

    def test_listDatasets(self):
        """  listDatasets (DQ2 CLIENT): """
        assert(False)

    def test_listDatasets2(self):
        """  listDatasets2 (DQ2 CLIENT): """
        assert(False)

    def test_listDatasetsByCreationDate(self):
        """  listDatasetsByCreationDate (DQ2 CLIENT): """
        assert(False)

    def test_listDatasetsByGUIDs(self):
        """  listDatasetsByGUIDs (DQ2 CLIENT): """
        assert(False)

    def test_listDatasetsByMetaData(self):
        """  listDatasetsByMetaData (DQ2 CLIENT): """
        assert(False)

    def test_listDatasetsByNameInSite(self):
        """  listDatasetsByNameInSite (DQ2 CLIENT): """
        assert(False)

    def test_listDatasetsInContainer(self):
        """  listDatasetsInContainer (DQ2 CLIENT): """
        assert(False)

    def test_listDatasetsInSite(self):
        """  listDatasetsInSite (DQ2 CLIENT): """
        assert(False)

    def test_listFileReplicas(self):
        """  listFileReplicas (DQ2 CLIENT): """
        assert(False)

    def test_listFileReplicasBySites(self):
        """  listFileReplicasBySites (DQ2 CLIENT): """
        assert(False)

    def test_listFilesInDataset(self):
        """  listFilesInDataset (DQ2 CLIENT): """
        assert(False)

    def test_listMetaDataAttributes(self):
        """  listMetaDataAttributes (DQ2 CLIENT): """
        assert(False)

    def test_listMetaDataReplica(self):
        """  listMetaDataReplica (DQ2 CLIENT): """
        assert(False)

    def test_listSubscriptionInfo(self):
        """  listSubscriptionInfo (DQ2 CLIENT): """
        assert(False)

    def test_listSubscriptions(self):
        """  listSubscriptions (DQ2 CLIENT): """
        assert(False)

    def test_listSubscriptionsInSite(self):
        """  listSubscriptionsInSite (DQ2 CLIENT): """
        assert(False)

    def test_listSuspiciousFiles(self):
        """  listSuspiciousFiles (DQ2 CLIENT): """
        assert(False)

    def test_ping(self):
        """  ping (DQ2 CLIENT): """
        assert(False)

    def test_queryReplicaHistory(self):
        """  queryReplicaHistory (DQ2 CLIENT): """
        assert(False)

    def test_queryStorageUsage(self):
        """  queryStorageUsage (DQ2 CLIENT): """
        assert(False)

    def test_queryStorageUsageHistory(self):
        """  queryStorageUsageHistory (DQ2 CLIENT): """
        assert(False)

    def test_registerContainer(self):
        """  registerContainer (DQ2 CLIENT): """
        assert(False)

    def test_registerDatasetLocation(self):
        """  registerDatasetLocation (DQ2 CLIENT): """
        assert(False)

    def test_registerDatasetSubscription(self):
        """  registerDatasetSubscription (DQ2 CLIENT): """
        assert(False)

    def test_registerDatasetsInContainer(self):
        """  registerDatasetsInContainer (DQ2 CLIENT): """
        assert(False)

    def test_registerFilesInDataset(self):
        """  registerFilesInDataset (DQ2 CLIENT): """
        assert(False)

    def test_registerFilesInDatasets(self):
        """  registerFilesInDatasets (DQ2 CLIENT): """
        assert(False)

    def test_registerNewDataset(self):
        """  registerNewDataset (DQ2 CLIENT): """
        assert(False)

    def test_registerNewDataset2(self):
        """  registerNewDataset2 (DQ2 CLIENT): """
        assert(False)

    def test_registerNewVersion(self):
        """  registerNewVersion (DQ2 CLIENT): """
        assert(False)

    def test_registerNewVersion2(self):
        """  registerNewVersion2 (DQ2 CLIENT): """
        assert(False)

    def test_resetSubscription(self):
        """  resetSubscription (DQ2 CLIENT): """
        assert(False)

    def test_resetSubscriptionsInSite(self):
        """  resetSubscriptionsInSite (DQ2 CLIENT): """
        assert(False)

    def test_searchDatasets(self):
        """  searchDatasets (DQ2 CLIENT): """
        assert(False)

    def test_setDatasetReplicaToDeleted(self):
        """  setDatasetReplicaToDeleted (DQ2 CLIENT): """
        assert(False)

    def test_setMetaDataAttribute(self):
        """  setMetaDataAttribute (DQ2 CLIENT): """
        assert(False)

    def test_setReplicaMetaDataAttribute(self):
        """  setReplicaMetaDataAttribute (DQ2 CLIENT): """
        assert(False)

    def test_updateCompleteness(self):
        """  updateCompleteness (DQ2 CLIENT): """
        assert(False)

    def test_verifyFilesInDataset(self):
        """  verifyFilesInDataset (DQ2 CLIENT): """
        assert(False)
