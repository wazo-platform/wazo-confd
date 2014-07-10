# -*- coding: UTF-8 -*-
#
# Copyright (C) 2013  Avencall
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

from xivo_restapi.authentication import auth
from xivo_restapi.negotiate.flask_negotiate import produces, consumes


class RouteGenerator(object):

    def __init__(self, blueprint):
        self._blueprint = blueprint

    def __call__(self, route, *args, **kwargs):
        def decorator(func):
            func = auth.login_required(func)
            func = produces('application/json')(func)
            # func = consumes('application/json')(func)  # Blocks requests with no Content-Type, even if not needed
            # MUST BE CALLED AS THE END
            self._blueprint.route(route, *args, **kwargs)(func)
        return decorator
