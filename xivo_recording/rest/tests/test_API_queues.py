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


from mock import Mock, patch
from xivo_recording.recording_config import RecordingConfig
from xivo_recording.rest import rest_encoder
from xivo_recording.services.queue_management import QueueManagement
import unittest

mock_queue_management = Mock(QueueManagement)


class TestFlaskHttpRoot(unittest.TestCase):

    def setUp(self):

        self.patcher = patch("xivo_recording.services." +\
                             "queue_management.QueueManagement")

        mock = self.patcher.start()
        self.instance_queue_management = mock_queue_management
        mock.return_value = self.instance_queue_management

        from xivo_recording.rest import flask_http_server
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    def tearDown(self):
        self.patcher.stop()

    def test_list_queues(self):
        status = "200 OK"
        liste = [{"number": "1"},
                 {"number": "3"},
                 {"number": "2"}]
        self.instance_queue_management.get_all_queues\
                    .return_value = liste
        result = self.app.get(RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RecordingConfig.XIVO_QUEUES_SERVICE_PATH + '/',
                              '')

        self.instance_queue_management.get_all_queues\
                    .assert_any_call()
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)
        liste = sorted(liste, key=lambda k: k['number'])
        self.assertListEqual(liste,
                             rest_encoder.decode(result.data),
                             "Result is not the expected one: "\
                                + str(result.data))

    def test_list_queues_error(self):
        status = "500 INTERNAL SERVER ERROR"

        def mock_get_all_queues():
            raise Exception()

        self.instance_queue_management.get_all_queues\
                    .side_effect = mock_get_all_queues
        result = self.app.get(RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RecordingConfig.XIVO_QUEUES_SERVICE_PATH + '/',
                              '')

        self.instance_queue_management.get_all_queues\
                    .assert_any_call()
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)
        self.instance_queue_management.get_all_queues\
                    .side_effect = None
