# -*- coding: utf-8 -*-
# Copyright 2014-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from functools import wraps

import requests

from flask_httpauth import HTTPDigestAuth

from xivo.auth_verifier import AuthVerifier, required_acl

logger = logging.getLogger(__name__)

required_acl = required_acl


class Authentication(HTTPDigestAuth):

    def __init__(self):
        super(Authentication, self).__init__()
        self.auth_verifier = AuthVerifier()
        self._auth_host = None
        self._auth_port = None

    def set_config(self, config):
        self._auth_host = config['auth']['host']
        self._auth_port = config['auth']['port']
        self.auth_verifier.set_config(config['auth'])

    def login_required(self, func):
        auth_func = super(Authentication, self).login_required(func)

        @wraps(func)
        def decorated(*args, **kwargs):
            if self._verify_token(func, *args, **kwargs):
                return func(*args, **kwargs)
            return auth_func(*args, **kwargs)

        return decorated

    def _verify_token(self, func, *args, **kwargs):
        try:
            token = self.auth_verifier.token()
            current_required_acl = self.auth_verifier.acl(func, *args, **kwargs)
            token_is_valid = self.auth_verifier.client().token.is_valid(token, current_required_acl)
        except requests.RequestException as e:
            logger.error('Authentication server on %s:%s unreachable: %s',
                         self._auth_host, self._auth_port, e)
            return False

        return token_is_valid


authentication = Authentication()
