# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from werkzeug.local import LocalProxy as Proxy

from flask import g
from requests import HTTPError
from wazo_auth_client import Client as AuthClient
from xivo_dao.helpers.exception import ServiceError

logger = logging.getLogger(__name__)

auth_config = {}


class AuthClientProxy:
    def __init__(self, auth_client):
        self._auth_client = auth_client
        self._users_created = []
        self.users = self._auth_client.users

    def new_user(self, *args, **kwargs):
        try:
            user = self._auth_client.users.new(*args, **kwargs)
        except HTTPError as e:
            raise ServiceError(str(e))

        self._users_created.append(user)
        return user

    def edit_user(self, *args, **kwargs):
        # rollback system can be added here
        self.auth_client.users.edit(*args, **kwargs)

    def rollback(self):
        for user in self._users_created:
            self._auth_client.users.delete(user['uuid'])

    @classmethod
    def from_config(cls, *args, **kwargs):
        client = AuthClient(*args, **kwargs)
        # 30 minutes should be enought to import all users
        token = client.token.new(expiration=30 * 30)['token']
        client.set_token(token)
        return cls(client)


def get_auth_client():
    client = g.get('auth_client_user_import')
    if not client:
        client = g.auth_client_user_import = AuthClientProxy.from_config(**auth_config)
    return client


def set_auth_client_config(config):
    global auth_config
    auth_config = config


auth_client = Proxy(get_auth_client)
