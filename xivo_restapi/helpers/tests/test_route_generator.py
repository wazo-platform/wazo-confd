# -*- coding: UTF-8 -*-

# Copyright (C) 2013 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import unittest

from flask import Blueprint
from mock import Mock, patch

from xivo_restapi.helpers.route_generator import RouteGenerator


class TestRouteGenerator(unittest.TestCase):

    @patch('xivo_restapi.helpers.route_generator.consumes')
    @patch('xivo_restapi.helpers.route_generator.produces')
    @patch('xivo_restapi.helpers.route_generator.auth')
    def test_route_generator(self, auth, produces, consumes):
        # WARNING : You are not expected to understand this the first time.
        # Go read up on how parameterized decorators work in python
        #
        # This test checks that an action is wrapped in 3 decorators
        # (exception_catcher, requires_auth, produces) and the order in
        # which the decorators are called.

        def action():
            pass

        blueprint = Mock(Blueprint)
        decorated_route = blueprint.route.return_value = Mock()

        route_generator = RouteGenerator(blueprint)

        decorated_login_required = auth.login_required.return_value = Mock()
        parameterized_produces = produces.return_value = Mock()
        decorated_produces = parameterized_produces.return_value = Mock()

        route_generator('')(action)

        auth.login_required.assert_called_once_with(action)

        produces.assert_called_once_with('application/json')
        parameterized_produces.assert_called_once_with(decorated_login_required)

        blueprint.route.assert_called_once_with('')
        decorated_route.assert_called_once_with(decorated_produces)
