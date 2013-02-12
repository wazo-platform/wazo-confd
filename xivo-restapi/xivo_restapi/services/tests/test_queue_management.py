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

from mock import Mock
from xivo_dao import queue_dao
from xivo_dao.alchemy.queuefeatures import QueueFeatures
import unittest


class SampleClass:

    def __init__(self):
        self.id = 1


class TestQueueManagement(unittest.TestCase):

    def setUp(self):
        from xivo_restapi.services.queue_management import QueueManagement
        self._queueManager = QueueManagement()

    def test_get_all_queues(self):
        queue_dao.all_queues = Mock()
        data = [QueueFeatures()]
        queue_dao.all_queues.return_value = data
        result = self._queueManager.get_all_queues()
        self.assertEquals(result, data)
