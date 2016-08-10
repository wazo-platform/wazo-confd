# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

import collections
import json
import logging

from flask.ext.restful import Resource
from pkg_resources import resource_string, iter_entry_points

logger = logging.getLogger(__name__)


class SwaggerResource(Resource):

    api_filename = "api.json"

    def get(self):
        api_spec = {}
        for module in iter_entry_points(group='xivo_confd.plugins'):
            try:
                spec = json.loads(resource_string(module.module_name, self.api_filename))
                api_spec = self.update(api_spec, spec)
            except IOError:
                logger.debug('API spec for module "%s" does not exist', module.module_name)

        if not api_spec.get('info'):
            return {'error': "API spec does not exist"}, 404

        return api_spec

    def update(self, a, b):
        for key, value in b.iteritems():
            if isinstance(value, collections.Mapping):
                result = self.update(a.get(key, {}), value)
                a[key] = result
            else:
                a[key] = b[key]
        return a
