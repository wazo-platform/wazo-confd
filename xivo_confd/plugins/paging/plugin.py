# -*- coding: UTF-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from .service import build_service
from .resource import PagingItem, PagingList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(PagingList,
                         '/pagings',
                         resource_class_args=(service,)
                         )

        api.add_resource(PagingItem,
                         '/pagings/<int:id>',
                         endpoint='pagings',
                         resource_class_args=(service,)
                         )
