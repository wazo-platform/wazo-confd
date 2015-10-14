# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_dao.alchemy.usersip import UserSIP as SIP
from xivo_dao.alchemy.linefeatures import LineFeatures as Line


class LineSip(object):

    def __init__(self,
                 context,
                 id=None,
                 username=None,
                 secret=None,
                 callerid=None,
                 provisioning_extension=None,
                 device_slot=1):
        self.id = id
        self.username = username
        self.secret = secret
        self.callerid = callerid
        self.provisioning_extension = provisioning_extension
        self.device_slot = device_slot
        self.context = context

    @classmethod
    def from_line_and_sip(cls, line, sip):
        return cls(id=line.id,
                   context=line.context,
                   username=sip.username,
                   secret=sip.secret,
                   callerid=sip.callerid,
                   provisioning_extension=line.provisioning_code,
                   device_slot=line.position)

    def build_sip(self):
        return SIP(username=self.username,
                   secret=self.secret,
                   callerid=self.callerid,
                   context=self.context)

    def build_line(self, sip):
        return Line(position=self.device_slot,
                    provisioning_code=self.provisioning_extension,
                    context=self.context,
                    protocol='sip',
                    protocolid=sip.id)

    def update_sip(self, sip):
        sip.username = self.username
        sip.secret = self.secret
        sip.callerid = self.callerid
        sip.context = self.context

    def update_line(self, line):
        line.position = self.device_slot
        line.context = self.context
        line.provisioning_code = self.provisioning_extension
