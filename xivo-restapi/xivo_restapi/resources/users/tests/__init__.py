# -*- coding: UTF-8 -*-
#
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from functools import wraps
from mock import Mock
from xivo_restapi.authentication import xivo_realm_digest
from xivo_restapi.negotiate import flask_negotiate


def mock_basic_decorator(func):
    return func


def mock_parameterized_decorator(string):
    def decorated(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorated

xivo_realm_digest.realmDigest = Mock()
xivo_realm_digest.realmDigest.requires_auth.side_effect = mock_basic_decorator
flask_negotiate.consumes = Mock()
flask_negotiate.consumes.side_effect = mock_parameterized_decorator
flask_negotiate.produces = Mock()
flask_negotiate.produces.side_effect = mock_parameterized_decorator
