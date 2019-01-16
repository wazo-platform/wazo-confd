# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_confd.auth import required_acl
from xivo_confd.helpers.asterisk import AsteriskConfigurationList


class ConfBridgeWazoDefaultBridgeList(AsteriskConfigurationList):
    section_name = 'wazo_default_bridge'

    @required_acl('confd.asterisk.confbridge.wazo_default_bridge.get')
    def get(self):
        return super(ConfBridgeWazoDefaultBridgeList, self).get()

    @required_acl('confd.asterisk.confbridge.wazo_default_bridge.update')
    def put(self):
        return super(ConfBridgeWazoDefaultBridgeList, self).put()


class ConfBridgeWazoDefaultUserList(AsteriskConfigurationList):
    section_name = 'wazo_default_user'

    @required_acl('confd.asterisk.confbridge.wazo_default_user.get')
    def get(self):
        return super(ConfBridgeWazoDefaultUserList, self).get()

    @required_acl('confd.asterisk.confbridge.wazo_default_user.update')
    def put(self):
        return super(ConfBridgeWazoDefaultUserList, self).put()
