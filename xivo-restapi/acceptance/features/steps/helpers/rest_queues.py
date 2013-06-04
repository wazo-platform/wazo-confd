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

import random
import traceback

from acceptance.features.steps.helpers.ws_utils import WsUtils
from xivo_dao import queue_dao
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_restapi.restapi_config import RestAPIConfig


class RestQueues(object):

    def __init__(self):
        self.queue = QueueFeatures()
        self.ws_utils = WsUtils()

    def create(self, queue_name, queue_id=None):
        alea = random.randint(10000, 99999999)

        if queue_id is None:
            self.queue.id = str(alea)

        self.queue.name = queue_name + str(alea)
        self.queue.displayname = queue_name
        try:
            queue_dao.add_queue(self.queue)
        except Exception as e:
            traceback.print_exc()
            raise e
        return True

    def create_if_not_exists(self, queue_name, queue_id):
        try:
            queue_dao.get(queue_id)
            return True
        except LookupError:
            return self.create(queue_name, queue_id)
        except Exception as e:
            traceback.print_exc()
            raise e

    def find(self, columnName, searchItem):
        queues_result = self.ws_utils.rest_get(RestAPIConfig.XIVO_QUEUES_SERVICE_PATH + '/')

        queues = queues_result.data
        assert len(queues) > 0

        result = False
        for queue in queues:
            if queue[columnName].startswith(searchItem):
                result = True
                break

        return result
