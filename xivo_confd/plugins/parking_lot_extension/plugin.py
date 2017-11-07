# -*- coding: utf-8 -*-
#
# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.parking_lot import dao as parking_lot_dao
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd import api
from .resource import ParkingLotExtensionItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(ParkingLotExtensionItem,
                         '/parkinglots/<int:parking_lot_id>/extensions/<int:extension_id>',
                         endpoint='parking_lot_extensions',
                         resource_class_args=(service, parking_lot_dao, extension_dao))
