# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.outcall import dao as outcall_dao
from xivo_dao.resources.trunk import dao as trunk_dao

from xivo_confd import api
from .resource import OutcallTrunkList
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(OutcallTrunkList,
                         '/outcalls/<int:outcall_id>/trunks',
                         resource_class_args=(service, outcall_dao, trunk_dao)
                         )
