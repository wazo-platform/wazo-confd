# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.device.builder import (build_dao,
                                               build_service)

from xivo_confd.plugins.device.resource import (DeviceItem,
                                                DeviceList,
                                                DeviceAutoprov,
                                                DeviceSynchronize)


class Plugin(object):
    def load(self, core):
        provd_client = core.provd_client()

        dao = build_dao(provd_client)
        service = build_service(dao)

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
