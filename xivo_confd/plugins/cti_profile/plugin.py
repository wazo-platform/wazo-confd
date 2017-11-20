# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.cti_profile.service import build_service
from xivo_confd.plugins.cti_profile.resource import CtiProfileItem, CtiProfileList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(CtiProfileList,
                         '/cti_profiles',
                         resource_class_args=(service,)
                         )

        api.add_resource(CtiProfileItem,
                         '/cti_profiles/<int:id>',
                         endpoint='cti_profiles',
                         resource_class_args=(service,)
                         )
