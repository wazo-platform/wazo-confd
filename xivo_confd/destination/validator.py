# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from xivo_dao.resources.conference import dao as conference_dao
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.ivr import dao as ivr_dao
from xivo_dao.resources.outcall import dao as outcall_dao
from xivo_dao.resources.queue import dao as queue_dao
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao

from xivo_confd.helpers.validator import GetResource, ResourceExists


class DestinationValidator(object):

    _VALIDATORS = {
        'application:callbackdisa': [],
        'application:directory': [],
        'application:disa': [],
        'application:faxtomail': [],
        'application:voicemailmain': [],
        'custom': [],
        'extension': [],
        'group': [ResourceExists('actionarg1', group_dao.exists, 'Group')],
        'endcall:busy': [],
        'endcall:congestion': [],
        'endcall:hangup': [],
        'ivr': [ResourceExists('actionarg1', ivr_dao.get, 'IVR')],
        'meetme': [ResourceExists('actionarg1', conference_dao.exists, 'Conference')],
        'none': [],
        'outcall': [GetResource('actionarg1', outcall_dao.get, 'Outcall')],
        'queue': [ResourceExists('actionarg1', queue_dao.exists, 'Queue')],
        'sound': [],
        'user': [GetResource('actionarg1', user_dao.get, 'User')],
        'voicemail': [GetResource('actionarg1', voicemail_dao.get, 'Voicemail')],
    }

    def validate(self, destination):
        for validator in self._VALIDATORS[destination.action]:
            validator.validate(destination)
