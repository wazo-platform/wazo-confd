# -*- coding: UTF-8 -*-
# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from .service import build_service
from .resource import ParkingLotItem, ParkingLotList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(ParkingLotList,
                         '/parkinglots',
                         resource_class_args=(service,)
                         )

        api.add_resource(ParkingLotItem,
                         '/parkinglots/<int:id>',
                         endpoint='parkinglots',
                         resource_class_args=(service,)
                         )
