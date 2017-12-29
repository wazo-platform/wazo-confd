# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import (
    FeaturesApplicationmapList,
    FeaturesFeaturemapList,
    FeaturesGeneralList,
)
from .service import build_service


class Plugin(object):

    def load(self, core):
        api = core.api
        service = build_service()

        api.add_resource(
            FeaturesApplicationmapList,
            '/asterisk/features/applicationmap',
            resource_class_args=(service,)
        )

        api.add_resource(
            FeaturesFeaturemapList,
            '/asterisk/features/featuremap',
            resource_class_args=(service,)
        )

        api.add_resource(
            FeaturesGeneralList,
            '/asterisk/features/general',
            resource_class_args=(service,)
        )