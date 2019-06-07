# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import (
    FeaturesApplicationmapList,
    FeaturesFeaturemapList,
    FeaturesGeneralList,
)
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
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
