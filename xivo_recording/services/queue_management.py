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

from xivo_dao import queue_dao
from xivo_recording.dao.helpers.dynamic_formatting import \
    table_list_to_list_dict
from xivo_recording.services.manager_utils import _init_db_connection, \
    reconnectable
import logging

logger = logging.getLogger(__name__)


class QueueManagement:

    def __init__(self):
        _init_db_connection()

    @reconnectable(None)
    def get_all_queues(self):
        result = queue_dao.all_queues()
        if result != None:
            return table_list_to_list_dict(result)
        return False
