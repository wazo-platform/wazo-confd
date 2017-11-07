# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao

from xivo_confd import api
from xivo_confd.plugins.user_voicemail.service import build_service
from xivo_confd.plugins.user_voicemail.resource import (UserVoicemailItem,
                                                        UserVoicemailList,
                                                        VoicemailUserList,
                                                        UserVoicemailLegacy)


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(VoicemailUserList,
                         '/voicemails/<int:voicemail_id>/users',
                         resource_class_args=(service, user_dao, voicemail_dao))

        api.add_resource(UserVoicemailList,
                         '/users/<int:user_id>/voicemails',
                         '/users/<uuid:user_id>/voicemails',
                         endpoint='user_voicemails',
                         resource_class_args=(service, user_dao, voicemail_dao))

        api.add_resource(UserVoicemailItem,
                         '/users/<int:user_id>/voicemails/<int:voicemail_id>',
                         '/users/<uuid:user_id>/voicemails/<int:voicemail_id>',
                         resource_class_args=(service, user_dao, voicemail_dao))

        api.add_resource(UserVoicemailLegacy,
                         '/users/<int:user_id>/voicemail',
                         '/users/<uuid:user_id>/voicemail',
                         resource_class_args=(service, user_dao, voicemail_dao))
