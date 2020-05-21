# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.asterisk import AsteriskConfigurationList


class HEPGeneralList(AsteriskConfigurationList):
    section_name = 'general'

    @required_acl('confd.asterisk.hep.general.get')
    def get(self):
        return super().get()

    @required_acl('confd.asterisk.hep.general.update')
    def put(self):
        return super().put()
