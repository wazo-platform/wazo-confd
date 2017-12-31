# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import SipItem, SipList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        provd_client = dependencies['provd_client']()

        service = build_service(provd_client)

        api.add_resource(
            SipItem,
            '/endpoints/sip/<int:id>',
            endpoint='endpoint_sip',
            resource_class_args=(service,)
        )
        api.add_resource(
            SipList,
            '/endpoints/sip',
            resource_class_args=(service,)
        )
