# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from flask import Blueprint
from xivo_confd import config

import json
from pkg_resources import resource_string

PACKAGE = 'xivo_confd.resources.api'


def load(core_rest_api):
    blueprint = Blueprint('api', __name__, url_prefix='/%s/api' % config.API_VERSION)
    blueprint.add_url_rule('/api.json', 'api', api)
    core_rest_api.register(blueprint)


def api():
    try:
        api_spec = resource_string(PACKAGE, 'api.json')
    except IOError:
        msg = json.dumps(["API spec does not exist"])
        return (msg, 404)
    return (api_spec, 200, {'Content-Type': 'application/json'})
