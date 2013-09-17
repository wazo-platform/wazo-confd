# -*- coding: UTF-8 -*-

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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..


from mock import patch, Mock
from xivo_dao.alchemy.queuefeatures import QueueFeatures
from xivo_restapi.v1_0 import rest_encoder
from xivo_restapi.v1_0.restapi_config import RestAPIConfig
from xivo_restapi.v1_0.services.queue_management import QueueManagement
from xivo_restapi.v1_0.rest.tests.test_API import TestAPI

BASE_URL = "%s%s/" % (RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH, RestAPIConfig.XIVO_QUEUES_SERVICE_PATH)


class TestAPIQueues(TestAPI):

    @classmethod
    def setUpClass(cls):
        cls.patcher_queue = patch("xivo_restapi.v1_0.rest.API_queues.QueueManagement")
        mock_queue = cls.patcher_queue.start()
        cls.instance_queue_management = Mock(QueueManagement)
        mock_queue.return_value = cls.instance_queue_management

        TestAPI.setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.patcher_queue.stop()

    def test_list_queues(self):
        status = "200 OK"
        queue1 = QueueFeatures()
        queue1.number = '1'
        queue2 = QueueFeatures()
        queue2.number = '2'
        liste = [queue1, queue2]
        self.instance_queue_management.get_all_queues.return_value = liste
        result = self.app.get(BASE_URL, '')

        self.instance_queue_management.get_all_queues.assert_any_call()
        self.assertEquals(result.status, status)
        liste = sorted(liste, key=lambda k: k.number)
        self.assertEquals(rest_encoder.encode(liste), result.data)

    def test_list_queues_error(self):
        status = "500 INTERNAL SERVER ERROR"

        self.instance_queue_management.get_all_queues.side_effect = Exception
        result = self.app.get(BASE_URL, '')

        self.instance_queue_management.get_all_queues.assert_any_call()
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status: %s" % result.status)
        self.instance_queue_management.get_all_queues.side_effect = None
