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

from xivo_dao.helpers.db_manager import Base
from xivo_dao.service_data_model.base_sdm import BaseSdm
import json
import logging

logger = logging.getLogger()


decode = json.loads


def encode(data):
    result = data
    if(isinstance(data, tuple)):
        result = _process_paginated_data(data)
    return_value = json.dumps(result, default=_serialize)
    return return_value


def _process_paginated_data(data):
    (total, items) = data
    result = {'total': total,
              'items': items}
    return result


def _serialize(obj):
    if(isinstance(obj, Base)):
        result = obj.todict()
        missing_attributes = [item for item in obj.__dict__.keys() if item not in result and not item.startswith('_')]
        for attribute in missing_attributes:
            result[attribute] = getattr(obj, attribute)
        return result
    elif(isinstance(obj, BaseSdm)):
        return obj.todict()
    else:
        return str(obj)
