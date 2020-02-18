# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class PJSIPDocList(ConfdResource):
    def __init__(self, pjsip_doc):
        self._pjsip_doc = pjsip_doc

    @required_acl('confd.asterisk.pjsip.doc.read')
    def get(self):
        return self._pjsip_doc.get()
