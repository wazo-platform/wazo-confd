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


from xivo_confd import api
from xivo_confd.plugins.device.builder import (build_dao,
                                               build_service,
                                               build_device_updater,
                                               build_line_device_associator)

from xivo_confd.plugins.device.resource import (DeviceItem,
                                                DeviceList,
                                                DeviceAutoprov,
                                                DeviceSynchronize,
                                                LineDeviceAssociation,
                                                LineDeviceDissociation)


class Plugin(object):
    def load(self, core):
        provd_client = core.provd_client()

        dao = build_dao(provd_client)
        service = build_service(dao)

        device_updater = build_device_updater(provd_client)
        association_service = build_line_device_associator(device_updater)

        api.add_resource(DeviceItem,
                         '/devices/<id>',
                         endpoint='devices',
                         resource_class_args=(service,)
                         )

        api.add_resource(DeviceList,
                         '/devices',
                         resource_class_args=(service,)
                         )

        api.add_resource(DeviceAutoprov,
                         '/devices/<id>/autoprov',
                         resource_class_args=(service,)
                         )

        api.add_resource(DeviceSynchronize,
                         '/devices/<id>/synchronize',
                         resource_class_args=(service,)
                         )

        api.add_resource(LineDeviceAssociation,
                         '/devices/<device_id>/associate_line/<int:line_id>',
                         resource_class_args=(service, association_service)
                         )

        api.add_resource(LineDeviceDissociation,
                         '/devices/<device_id>/remove_line/<int:line_id>',
                         resource_class_args=(service, association_service)
                         )
