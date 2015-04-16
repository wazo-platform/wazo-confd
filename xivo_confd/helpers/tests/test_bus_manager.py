# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

import unittest
from xivo_confd.helpers.bus_manager import BusContext


class TestBusContext(unittest.TestCase):

    def test_new_from_config(self):
        config = {
            'bus': {
                'host': 'example.org',
                'port': 5672,
                'username': 'foo',
                'password': 'bar',
                'exchange_name': 'xivo',
                'exchange_type': 'topic',
            },
            'uuid': '111-2222',
        }

        bus_context = BusContext.new_from_config(config)

        self.assertEqual(bus_context._url, 'amqp://foo:bar@example.org:5672//')
