# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging
import requests

from flask import request
from flask_httpauth import HTTPDigestAuth
from functools import wraps

from xivo_dao import accesswebservice_dao
from xivo.auth_verifier import AuthVerifier, required_acl


logger = logging.getLogger(__name__)

required_acl = required_acl


class ConfdAuth(HTTPDigestAuth):

    ALLOWED_HOSTS = ['127.0.0.1']

    def __init__(self):
        super(ConfdAuth, self).__init__()
        self.get_password(accesswebservice_dao.get_password)
        self.auth_verifier = AuthVerifier()
        self._auth_host = None
        self._auth_port = None

    def set_config(self, config):
        self._auth_host = config['host']
        self._auth_port = config['port']
        self.auth_verifier.set_config(config)

    def login_required(self, func):
        auth_func = super(ConfdAuth, self).login_required(func)

        @wraps(func)
        def decorated(*args, **kwargs):
            if self._remote_address_allowed():
                return func(*args, **kwargs)
            elif self._verify_token(func, *args, **kwargs):
                return func(*args, **kwargs)
            return auth_func(*args, **kwargs)

        return decorated

    def _remote_address_allowed(self):
        # check localhost first to avoid accessing the database for nothing
        remote_addr = request.remote_addr
        if remote_addr in self.ALLOWED_HOSTS:
            return True
        return remote_addr in accesswebservice_dao.get_allowed_hosts()

    def _verify_token(self, func, *args, **kwargs):
        try:
            token = self.auth_verifier.token()
            required_acl = self._acl(func, *args, **kwargs)
            token_is_valid = self.auth_verifier.client().token.is_valid(token, required_acl)
        except requests.RequestException as e:
            message = 'Authentication server on {host}:{port} unreachable: {error}'
            logger.error(message.format(host=self._auth_host, port=self._auth_port, error=e))
            return False

        return token_is_valid

    def _acl(self, func, *args, **kwargs):
        required_acl = self.auth_verifier.acl(func, *args, **kwargs)
        if not required_acl:
            return 'confd.#'
        return required_acl


auth = ConfdAuth()
