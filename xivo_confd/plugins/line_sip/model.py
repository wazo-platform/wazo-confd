# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.usersip import UserSIP as SIP
from xivo_dao.alchemy.linefeatures import LineFeatures as Line


class LineSip:

    def __init__(self,
                 context,
                 tenant_uuid,
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
        self.tenant_uuid = tenant_uuid

    @classmethod
    def from_line_and_sip(cls, line, sip):
        return cls(id=line.id,
                   context=line.context,
                   tenant_uuid=sip.tenant_uuid,
                   username=sip.name,
                   secret=sip.secret,
                   callerid=sip.callerid,
                   provisioning_extension=line.provisioning_code,
                   device_slot=line.position)

    def build_sip(self):
        return SIP(name=self.username,
                   secret=self.secret,
                   callerid=self.callerid,
                   context=self.context,
                   tenant_uuid=self.tenant_uuid)

    def build_line(self, sip):
        return Line(position=self.device_slot,
                    provisioning_code=self.provisioning_extension,
                    context=self.context,
                    protocol='sip',
                    protocolid=sip.id)

    def update_sip(self, sip):
        sip.name = self.username
        sip.secret = self.secret
        sip.callerid = self.callerid
        sip.context = self.context

    def update_line(self, line):
        line.position = self.device_slot
        line.context = self.context
        line.provisioning_code = self.provisioning_extension
