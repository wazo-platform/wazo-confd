# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from test_api import confd
from test_api import config


def generate_extension(**parameters):
    parameters.setdefault('context', config.CONTEXT)
    if 'exten' not in parameters:
        parameters['exten'] = find_available_exten(parameters['context'])
    return add_extension(**parameters)


def find_available_exten(context, exclude=None):
    exclude = {int(n) for n in exclude} if exclude else set()
    response = confd.extensions.get()
    numbers = [int(e['exten'])
               for e in response.items
               if e['context'] == context and e['exten'].isdigit()]

    available = set(config.EXTENSION_RANGE) - set(numbers) - exclude
    return str(available.pop())


def add_extension(**params):
    response = confd.extensions.post(params)
    return response.item


def delete_extension(extension_id, check=False):
    response = confd.extensions(extension_id).delete()
    if check:
        response.assert_ok()
