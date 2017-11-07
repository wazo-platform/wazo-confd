# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_manager import Session
from xivo_dao.resources.voicemail import dao as voicemail_dao

from xivo_confd import sysconfd
from xivo_confd.helpers.resource import CRUDService
from xivo_confd.plugins.voicemail.notifier import build_notifier
from xivo_confd.plugins.voicemail.validator import build_validator


class VoicemailService(CRUDService):

    def __init__(self, dao, validator, notifier, sysconf, extra=None):
        super(VoicemailService, self).__init__(dao, validator, notifier, extra)
        self.sysconf = sysconf

    def edit(self, voicemail, updated_fields=None):
        old_number, old_context = voicemail.get_old_number_context()
        with Session.no_autoflush:
            self.validator.validate_edit(voicemail)
        self.dao.edit(voicemail)
        self.move_voicemail(voicemail, old_number, old_context)
        self.notifier.edited(voicemail)

    def delete(self, voicemail):
        self.validator.validate_delete(voicemail)
        self.dao.delete(voicemail)
        self.delete_voicemail(voicemail)
        self.notifier.deleted(voicemail)

    def delete_voicemail(self, voicemail):
        self.sysconf.delete_voicemail(voicemail.number,
                                      voicemail.context)

    def move_voicemail(self, voicemail, old_number, old_context):
        if (old_number != voicemail.number) or (old_context != voicemail.context):
            self.sysconf.move_voicemail(old_number, old_context,
                                        voicemail.number, voicemail.context)


def build_service():
    return VoicemailService(voicemail_dao,
                            build_validator(),
                            build_notifier(),
                            sysconfd)
