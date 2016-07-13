# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.call_permission import dao as call_permission_dao

from xivo_confd import api
from xivo_confd.plugins.user_call_permission.resource import UserCallPermissionAssociation
from xivo_confd.plugins.user_call_permission.resource import UserCallPermissionGet
from xivo_confd.plugins.user_call_permission.resource import CallPermissionUserGet

from xivo_confd.plugins.user_call_permission.service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(UserCallPermissionAssociation,
                         '/users/<uuid:user_id>/callpermissions/<int:call_permission_id>',
                         '/users/<int:user_id>/callpermissions/<int:call_permission_id>',
                         endpoint='user_call_permissions',
                         resource_class_args=(service, user_dao, call_permission_dao)
                         )

        api.add_resource(UserCallPermissionGet,
                         '/users/<uuid:user_id>/callpermissions',
                         '/users/<int:user_id>/callpermissions',
                         resource_class_args=(service, user_dao, call_permission_dao)
                         )

        api.add_resource(CallPermissionUserGet,
                         '/callpermissions/<int:call_permission_id>/users',
                         resource_class_args=(service, user_dao, call_permission_dao)
                         )
