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

from gevent import httplib
from xivo_dao import queue_features_dao
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_recording.recording_config import RecordingConfig
from xivo_recording.rest import rest_encoder
from xivo_recording.services.manager_utils import _init_db_connection
import random




class RestQueues:

    def __init__(self):
        self.queue = QueueFeatures()
        _init_db_connection()
        
    def create(self, queue_name):
        alea = random.randint(10000, 99999999)
        self.queue.id = str(alea)
        self.queue.name = queue_name + str(alea)
        self.queue.displayname = queue_name
        try:
            queue_features_dao.add_queue(self.queue);
        except Exception as e:
            print "got exception: ", e
            raise e
        return True
    
    def create_if_not_exists(self, queue_id):
        try:
            queue_features_dao.get(queue_id)
        except LookupError:
            self.queue.id = str(queue_id)
            self.queue.name = "test_lettuce" + str(queue_id)
            self.queue.displayname = self.queue.name
            try:
                queue_features_dao.add_queue(self.queue);
            except Exception as e:
                print "got exception: ", e
                raise e
            return True
        else:
            return True
        
    def list(self, columnName, searchItem):
        connection = RecordingConfig.getWSConnection()

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_QUEUES_SERVICE_PATH + "/"

        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        connection.request("GET", requestURI, "", headers)
        reply = connection.getresponse()
        body = reply.read()
        queues = rest_encoder.decode(body)
        assert len(queues) > 0
        result = False
        for queue in queues:
            if queue[columnName].startswith(searchItem):
                result = True
                break
        
        return result