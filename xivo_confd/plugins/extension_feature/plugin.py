# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import ExtensionFeatureItem, ExtensionFeatureList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']

        service = build_service()

        api.add_resource(
            ExtensionFeatureItem,
            '/extensions/features/<int:id>',
            endpoint='extensions_features',
            resource_class_args=(service,)
        )
        api.add_resource(
            ExtensionFeatureList,
            '/extensions/features',
            resource_class_args=(service,)
        )
