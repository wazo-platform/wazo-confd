# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import CtiProfileItem, CtiProfileList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            CtiProfileList,
            '/cti_profiles',
            resource_class_args=(service,)
        )

        api.add_resource(
            CtiProfileItem,
            '/cti_profiles/<int:id>',
            endpoint='cti_profiles',
            resource_class_args=(service,)
        )
