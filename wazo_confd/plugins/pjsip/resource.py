# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource
from wazo_confd.helpers.asterisk import AsteriskConfigurationList


class PJSIPDocList(ConfdResource):
    def __init__(self, pjsip_doc):
        self._pjsip_doc = pjsip_doc

    @required_acl('confd.asterisk.pjsip.doc.read')
    def get(self):
        return self._pjsip_doc.get()


class PJSIPGlobalList(AsteriskConfigurationList):
    section_name = 'global'

    @required_acl('confd.asterisk.pjsip.global.read')
    def get(self):
        return super().get()

    @required_acl('confd.asterisk.pjsip.global.update')
    def put(self):
        return super().put()


class PJSIPSystemList(AsteriskConfigurationList):
    section_name = 'system'

    @required_acl('confd.asterisk.pjsip.system.read')
    def get(self):
        return super().get()

    @required_acl('confd.asterisk.pjsip.system.update')
    def put(self):
        return super().put()
