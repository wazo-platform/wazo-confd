# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import api
from xivo_confd.plugins.voicemail.service import build_service
from xivo_confd.plugins.voicemail.resource import VoicemailItem, VoicemailList


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(VoicemailList,
                         '/voicemails',
                         resource_class_args=(service,)
                         )

        api.add_resource(VoicemailItem,
                         '/voicemails/<int:id>',
                         endpoint='voicemails',
                         resource_class_args=(service,)
                         )
