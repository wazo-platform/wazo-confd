# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from flask import current_app
from flask import request
from flask_httpauth import HTTPDigestAuth
from functools import wraps

from xivo_dao import accesswebservice_dao
from xivo_auth_client import Client as AuthClient


logger = logging.getLogger(__name__)


class ConfdAuth(HTTPDigestAuth):

    ALLOWED_HOSTS = ['127.0.0.1']

    def __init__(self):
        super(ConfdAuth, self).__init__()
        self.get_password(accesswebservice_dao.get_password)

    def login_required(self, func):
        auth_func = super(ConfdAuth, self).login_required(func)

        @wraps(func)
        def decorated(*args, **kwargs):
            if self._remote_address_allowed():
                return func(*args, **kwargs)
            elif self._valid_token():
                return func(*args, **kwargs)
            return auth_func(*args, **kwargs)

        return decorated

    def _remote_address_allowed(self):
        # check localhost first to avoid accessing the database for nothing
        remote_addr = request.access_route[0]
        if remote_addr in self.ALLOWED_HOSTS:
            return True
        return remote_addr in accesswebservice_dao.get_allowed_hosts()

    def _valid_token(self):
        auth_config = current_app.config['auth']
        token = request.headers.get('X-Auth-Token', '')
        try:
            return AuthClient(**auth_config).token.is_valid(token, required_acl='acl:confd')
        except requests.RequestException as e:
            message = 'Authentication server on {host}:{port} unreachable: {error}'
            logger.error(message.format(host=auth_config['host'], port=auth_config['port'], error=e))
            return False
