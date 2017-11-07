# -*- coding: utf-8 -*-

# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

import logging
import requests

from functools import wraps

from flask import request
from flask_httpauth import HTTPDigestAuth

from xivo_dao import accesswebservice_dao
from xivo.auth_verifier import AuthVerifier, required_acl


logger = logging.getLogger(__name__)

required_acl = required_acl


class ConfdAuth(HTTPDigestAuth):

    ALLOWED_HOST = '127.0.0.1'

    def __init__(self):
        super(ConfdAuth, self).__init__()
        self.get_password(accesswebservice_dao.get_password)
        self.auth_verifier = AuthVerifier()
        self._auth_host = None
        self._auth_port = None
        self._allowed_port = None

    def set_config(self, config):
        self._auth_host = config['auth']['host']
        self._auth_port = config['auth']['port']
        try:
            self._allowed_port = str(config['rest_api']['http']['port'])
        except KeyError:
            pass  # None is fine if http is not enabled
        self.auth_verifier.set_config(config['auth'])

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
        remote_addr = request.environ.get('werkzeug.proxy_fix.orig_remote_addr', request.remote_addr)
        remote_port = request.environ['SERVER_PORT']
        if remote_addr == self.ALLOWED_HOST and remote_port == self._allowed_port:
            return True
        return remote_addr in accesswebservice_dao.get_allowed_hosts()

    def _verify_token(self, func, *args, **kwargs):
        try:
            token = self.auth_verifier.token()
            current_required_acl = self._acl(func, *args, **kwargs)
            token_is_valid = self.auth_verifier.client().token.is_valid(token, current_required_acl)
        except requests.RequestException as e:
            logger.error('Authentication server on %s:%s unreachable: %s',
                         self._auth_host, self._auth_port, e)
            return False

        return token_is_valid

    def _acl(self, func, *args, **kwargs):
        current_required_acl = self.auth_verifier.acl(func, *args, **kwargs)
        if not current_required_acl:
            return 'confd.#'
        return current_required_acl


auth = ConfdAuth()
