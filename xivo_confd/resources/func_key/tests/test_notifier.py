# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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

from unittest import TestCase

from xivo_dao.resources.func_key.model import UserFuncKey, BSFilterFuncKey

from xivo_confd.resources.func_key import notifier

from mock import patch, Mock


class TestNotifier(TestCase):

    @patch('xivo_bus.resources.func_key.event.UserCreateFuncKeyEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_create_user_func_key(self, send_bus_event, UserCreateFuncKeyEvent):
        new_event = UserCreateFuncKeyEvent.return_value = Mock()

        func_key = UserFuncKey(id=1, user_id=2)

        notifier.created(func_key)

        UserCreateFuncKeyEvent.assert_called_once_with(func_key.id,
                                                       func_key.user_id)

        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)

    @patch('xivo_bus.resources.func_key.event.UserDeleteFuncKeyEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_delete_user_func_key(self, send_bus_event, UserDeleteFuncKeyEvent):
        new_event = UserDeleteFuncKeyEvent.return_value = Mock()

        func_key = UserFuncKey(id=1, user_id=2)

        notifier.deleted(func_key)

        UserDeleteFuncKeyEvent.assert_called_once_with(func_key.id,
                                                       func_key.user_id)

        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)

    @patch('xivo_bus.resources.func_key.event.BSFilterCreateFuncKeyEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_create_bsfilter_func_key(self, send_bus_event, BSFilterCreateFuncKeyEvent):
        new_event = BSFilterCreateFuncKeyEvent.return_value = Mock()

        func_key = BSFilterFuncKey(id=1, filter_id=2, secretary_id=3)

        notifier.created(func_key)

        BSFilterCreateFuncKeyEvent.assert_called_once_with(func_key.id,
                                                           func_key.filter_id,
                                                           func_key.secretary_id)

        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)

    @patch('xivo_bus.resources.func_key.event.BSFilterDeleteFuncKeyEvent')
    @patch('xivo_confd.helpers.bus_manager.send_bus_event')
    def test_delete_bsfilter_func_key(self, send_bus_event, BSFilterDeleteFuncKeyEvent):
        new_event = BSFilterDeleteFuncKeyEvent.return_value = Mock()

        func_key = BSFilterFuncKey(id=1, filter_id=2, secretary_id=3)

        notifier.deleted(func_key)

        BSFilterDeleteFuncKeyEvent.assert_called_once_with(func_key.id,
                                                           func_key.filter_id,
                                                           func_key.secretary_id)

        send_bus_event.assert_called_once_with(new_event, new_event.routing_key)
