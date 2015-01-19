# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Thomas Beermann, <thomas.beermann@cern.ch>, 2012-2013
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2012-2013
# - Cedric Serfon, <cedric.serfon@cern.ch>, 2014
# - Martin Barisits, <martin.barisits@cern.ch>, 2014
# - Cheng-Hsi Chao, <cheng-hsi.chao@cern.ch>, 2014
# - Ralph Vigne, <ralph.vigne@cern.ch>, 2015

from json import dumps
from requests.status_codes import codes

from rucio.client.baseclient import BaseClient
from rucio.client.baseclient import choice
from rucio.common.utils import build_url


class AccountClient(BaseClient):

    """Account client class for working with rucio accounts"""

    ACCOUNTS_BASEURL = 'accounts'

    def __init__(self, rucio_host=None, auth_host=None, account=None, ca_cert=None, auth_type=None, creds=None, timeout=None, user_agent='rucio-clients'):
        super(AccountClient, self).__init__(rucio_host, auth_host, account, ca_cert, auth_type, creds, timeout, user_agent)

    def add_account(self, account, type):
        """
        Sends the request to create a new account.

        :param account: the name of the account.
        :return: True if account was created successfully else False.
        :raises Duplicate: if account already exists.
        """

        data = dumps({'type': type})
        path = '/'.join([self.ACCOUNTS_BASEURL, account])
        url = build_url(choice(self.list_hosts), path=path)

        r = self._send_request(url, type='POST', data=data)

        if r.status_code == codes.created:
            return True
        else:
            exc_cls, exc_msg = self._get_exception(r.headers, r.status_code)
            raise exc_cls(exc_msg)

    def delete_account(self, account):
        """
        Sends the request to disable an account.

        :param account: the name of the account.
        :return: True is account was disabled successfully. False otherwise.
        :raises AccountNotFound: if account doesn't exist.
        """

        path = '/'.join([self.ACCOUNTS_BASEURL, account])
        url = build_url(choice(self.list_hosts), path=path)

        r = self._send_request(url, type='DEL')

        if r.status_code == codes.ok:
            return True
        else:
            exc_cls, exc_msg = self._get_exception(headers=r.headers, status_code=r.status_code)
            raise exc_cls(exc_msg)

    def get_account(self, account):
        """
        Sends the request to get information about a given account.

        :param account: the name of the account.
        :return: a list of attributes for the account. None if failure.
        :raises AccountNotFound: if account doesn't exist.
        """

        path = '/'.join([self.ACCOUNTS_BASEURL, account])
        url = build_url(choice(self.list_hosts), path=path)

        r = self._send_request(url)
        if r.status_code == codes.ok:
            acc = self._load_json_data(r)
            return acc.next()
        else:
            exc_cls, exc_msg = self._get_exception(headers=r.headers, status_code=r.status_code)
            raise exc_cls(exc_msg)

    def list_accounts(self, account_type=None, identity=None):
        """
        Sends the request to list all rucio accounts.

        :param type: The account type
        :param identity: The identity key name. For example x509 DN, or a username.

        :return: a list containing account info dictionary for all rucio accounts.
        :raises AccountNotFound: if account doesn't exist.
        """
        path = '/'.join([self.ACCOUNTS_BASEURL])
        url = build_url(choice(self.list_hosts), path=path)
        params = {}
        if account_type:
            params['account_type'] = account_type
        if identity:
            params['identity'] = identity

        r = self._send_request(url, params=params)

        if r.status_code == codes.ok:
            accounts = self._load_json_data(r)
            return accounts
        else:
            exc_cls, exc_msg = self._get_exception(headers=r.headers, status_code=r.status_code)
            raise exc_cls(exc_msg)

    def whoami(self):
        """
        Get information about account whose token is used

        :return: a list of attributes for the account. None if failure.
        :raises AccountNotFound: if account doesn't exist.
        """
        return self.get_account('whoami')

    def add_identity(self, account, identity, authtype, email, default=False):
        """
        Adds a membership association between identity and account.

        :param account: The account name.
        :param identity: The identity key name. For example x509 DN, or a username.
        :param authtype: The type of the authentication (x509, gss, userpass).
        :param default: If True, the account should be used by default with the provided identity.
        :param email: The Email address associated with the identity.
        """

        data = dumps({'identity': identity, 'authtype': authtype, 'default': default, 'email': email})
        path = '/'.join([self.ACCOUNTS_BASEURL, account, 'identities'])

        url = build_url(choice(self.list_hosts), path=path)

        r = self._send_request(url, type='POST', data=data)

        if r.status_code == codes.created:
            return True
        else:
            exc_cls, exc_msg = self._get_exception(headers=r.headers, status_code=r.status_code)
            raise exc_cls(exc_msg)

    def del_identity(self, account, identity, authtype, default=False):
        """
        Delete an identity's membership association with an account.

        :param account: The account name.
        :param identity: The identity key name. For example x509 DN, or a username.
        :param authtype: The type of the authentication (x509, gss, userpass).
        :param default: If True, the account should be used by default with the provided identity.
        """

        data = dumps({'identity': identity, 'authtype': authtype, 'default': default})
        path = '/'.join([self.ACCOUNTS_BASEURL, account, 'identities'])

        url = build_url(choice(self.list_hosts), path=path)

        r = self._send_request(url, type='DEL', data=data)

        if r.status_code == codes.ok:
            return True
        else:
            exc_cls, exc_msg = self._get_exception(headers=r.headers, status_code=r.status_code)
            raise exc_cls(exc_msg)

    def list_identities(self, account):
        """
        List all identities on an account.

        :param account: The account name.
        """
        path = '/'.join([self.ACCOUNTS_BASEURL, account, 'identities'])
        url = build_url(choice(self.list_hosts), path=path)
        r = self._send_request(url)
        if r.status_code == codes.ok:
            identities = self._load_json_data(r)
            return identities
        else:
            exc_cls, exc_msg = self._get_exception(r.headers, r.status_code)
            raise exc_cls(exc_msg)

    def list_account_rules(self, account):
        """
        List the associated rules of an account.

        :param account: The account name.
        """

        path = '/'.join([self.ACCOUNTS_BASEURL, account, 'rules'])
        url = build_url(choice(self.list_hosts), path=path)
        r = self._send_request(url, type='GET')
        if r.status_code == codes.ok:
            return self._load_json_data(r)
        else:
            exc_cls, exc_msg = self._get_exception(r.headers, r.status_code)
            raise exc_cls(exc_msg)

    def get_account_limits(self, account):
        """
        List the account rse limits of this account.

        :param account: The account name.
        """

        path = '/'.join([self.ACCOUNTS_BASEURL, account, 'limits'])
        url = build_url(choice(self.list_hosts), path=path)
        r = self._send_request(url, type='GET')
        if r.status_code == codes.ok:
            return self._load_json_data(r).next()
        else:
            exc_cls, exc_msg = self._get_exception(r.headers, r.status_code)
            raise exc_cls(exc_msg)

    def get_account_limit(self, account, rse):
        """
        List the account rse limits of this account for the specific rse.

        :param account: The account name.
        :param rse:     The rse name.
        """

        path = '/'.join([self.ACCOUNTS_BASEURL, account, 'limits', rse])
        url = build_url(choice(self.list_hosts), path=path)
        r = self._send_request(url, type='GET')
        if r.status_code == codes.ok:
            return self._load_json_data(r).next()
        else:
            exc_cls, exc_msg = self._get_exception(r.headers, r.status_code)
            raise exc_cls(exc_msg)

    def get_account_usage(self, account, rse=None):
        """
        List the account usage for one or all rses of this account.

        :param account: The account name.
        :param rse:     The rse name.
        """
        if rse:
            path = '/'.join([self.ACCOUNTS_BASEURL, account, 'usage', rse])
        else:
            path = '/'.join([self.ACCOUNTS_BASEURL, account, 'usage/'])
        url = build_url(choice(self.list_hosts), path=path)
        r = self._send_request(url, type='GET')
        if r.status_code == codes.ok:
            return self._load_json_data(r)
        else:
            exc_cls, exc_msg = self._get_exception(r.headers, r.status_code)
            raise exc_cls(exc_msg)
