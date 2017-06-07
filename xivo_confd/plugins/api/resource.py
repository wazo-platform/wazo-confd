# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

import logging
import yaml

from flask import make_response
from flask.ext.restful import Resource
from xivo.chain_map import ChainMap
from xivo.rest_api_helpers import load_all_api_specs

logger = logging.getLogger(__name__)


class SwaggerResource(Resource):

    api_filename = "api.yml"

    def __init__(self, config):
        self._enabled_plugins = config['enabled_plugins']

    def get(self):
        api_spec = ChainMap(*load_all_api_specs('xivo_confd.plugins', self.api_filename))

        if not api_spec.get('info'):
            return {'error': "API spec does not exist"}, 404

        return make_response(yaml.dump(api_spec), 200, {'Content-Type': 'application/x-yaml'})
