# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import RTPGeneralList, RTPIceHostCandidatesList
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            RTPGeneralList,
            '/asterisk/rtp/general',
            resource_class_args=(service,)
        )

        api.add_resource(
            RTPIceHostCandidatesList,
            '/asterisk/rtp/ice_host_candidates',
            resource_class_args=(service,)
        )
