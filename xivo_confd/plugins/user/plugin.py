# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from xivo_confd import api
from xivo_confd.plugins.user.service import build_service, build_service_callservice, build_service_forward
from xivo_confd.plugins.user.resource import UserItem, UserUuidItem, UserList
from xivo_confd.plugins.user.resource_sub import (UserServiceItem,
                                                  UserServiceList,
                                                  UserForwardItem,
                                                  UserForwardList)


class Plugin(object):

    def load(self, core):
        provd_client = core.provd_client()

        service = build_service(provd_client)
        service_callservice = build_service_callservice()
        service_forward = build_service_forward()

        api.add_resource(UserItem,
                         '/users/<int:id>',
                         endpoint='users',
                         resource_class_args=(service,)
                         )

        api.add_resource(UserUuidItem,
                         '/users/<uuid:uuid>',
                         resource_class_args=(service,)
                         )

        api.add_resource(UserList,
                         '/users',
                         resource_class_args=(service,)
                         )

        api.add_resource(UserServiceItem,
                         '/users/<uuid:user_id>/services/<service_name>',
                         '/users/<int:user_id>/services/<service_name>',
                         resource_class_args=(service_callservice,)
                         )

        api.add_resource(UserServiceList,
                         '/users/<uuid:user_id>/services',
                         '/users/<int:user_id>/services',
                         resource_class_args=(service_callservice,)
                         )

        api.add_resource(UserForwardItem,
                         '/users/<uuid:user_id>/forwards/<forward_name>',
                         '/users/<int:user_id>/forwards/<forward_name>',
                         resource_class_args=(service_forward,)
                         )

        api.add_resource(UserForwardList,
                         '/users/<uuid:user_id>/forwards',
                         '/users/<int:user_id>/forwards',
                         resource_class_args=(service_forward,)
                         )
