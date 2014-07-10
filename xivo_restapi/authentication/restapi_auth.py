# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from flask import request
from flask.ext.httpauth import HTTPDigestAuth
from functools import wraps
from xivo_dao import accesswebservice_dao

import logging
logger = logging.getLogger(__name__)


class RestApiAuth(HTTPDigestAuth):

    ALLOWED_HOSTS = ['127.0.0.1']

    def __init__(self):
        super(RestApiAuth, self).__init__()
        self.get_password(accesswebservice_dao.get_password)

    def login_required(self, func):
        auth_func = super(RestApiAuth, self).login_required(func)

        @wraps(func)
        def decorated(*args, **kwargs):
            if self._remote_address_allowed():
                return func(*args, **kwargs)
            return auth_func(*args, **kwargs)

        return decorated

    def _remote_address_allowed(self):
        hosts = accesswebservice_dao.get_allowed_hosts() + self.ALLOWED_HOSTS
        return request.remote_addr in hosts
