# -*- coding: UTF-8 -*-
# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from .service import build_service
from .resource import ConferenceItem, ConferenceList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(ConferenceList,
                         '/conferences',
                         resource_class_args=(service,)
                         )

        api.add_resource(ConferenceItem,
                         '/conferences/<int:id>',
                         endpoint='conferences',
                         resource_class_args=(service,)
                         )
