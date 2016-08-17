# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.resources.voicemail import dao as voicemail_dao

from xivo_confd import sysconfd
from xivo_confd.helpers.resource import CRUDService
from xivo_confd.plugins.voicemail.notifier import build_notifier
from xivo_confd.plugins.voicemail.validator import build_validator


class VoicemailService(CRUDService):

    def __init__(self, dao, validator, notifier, sysconf, extra=None):
        super(VoicemailService, self).__init__(dao, validator, notifier, extra)
        self.sysconf = sysconf

    def edit(self, voicemail, updated_fields=[]):
        self.validator.validate_edit(voicemail)
        old_voicemail = self.dao.get(voicemail.id)
        self.dao.edit(voicemail)
        self.move_voicemail(old_voicemail, voicemail)
        self.notifier.edited(voicemail)

    def delete(self, voicemail):
        self.validator.validate_delete(voicemail)
        self.dao.delete(voicemail)
        self.delete_voicemail(voicemail)
        self.notifier.deleted(voicemail)

    def delete_voicemail(self, voicemail):
        self.sysconf.delete_voicemail(voicemail.number,
                                      voicemail.context)

    def move_voicemail(self, old, new):
        if old.number_at_context != new.number_at_context:
            self.sysconf.move_voicemail(old.number, old.context,
                                        new.number, new.context)


def build_service():
    return VoicemailService(voicemail_dao,
                            build_validator(),
                            build_notifier(),
                            sysconfd)
