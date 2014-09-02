# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from xivo_dao.data_handler import errors


def map_to_api(mapping, data_dict):
    res = {}
    for model_key, api_key in mapping.iteritems():
        if model_key in data_dict:
            res[api_key] = data_dict[model_key]

    return res


def map_to_model(mapping, data_dict):
    validate_data_from_api(mapping, data_dict)
    res = {}
    for model_key, api_key in mapping.iteritems():
        if api_key in data_dict:
            res[model_key] = data_dict[api_key]

    return res


def validate_data_from_api(mapping, data_dict):
    unknown = []

    for api_key in data_dict.iterkeys():
        if api_key not in mapping.values():
            unknown.append(api_key)

    if unknown:
        raise errors.unknown(*unknown)
