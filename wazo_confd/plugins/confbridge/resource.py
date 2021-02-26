# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.asterisk import AsteriskConfigurationList


class ConfBridgeWazoDefaultBridgeList(AsteriskConfigurationList):
    section_name = 'wazo_default_bridge'

    @required_master_tenant()
    @required_acl('confd.asterisk.confbridge.wazo_default_bridge.get')
    def get(self):
        return super().get()

    @required_master_tenant()
    @required_acl('confd.asterisk.confbridge.wazo_default_bridge.update')
    def put(self):
        return super().put()


class ConfBridgeWazoDefaultUserList(AsteriskConfigurationList):
    section_name = 'wazo_default_user'

    @required_master_tenant()
    @required_acl('confd.asterisk.confbridge.wazo_default_user.get')
    def get(self):
        return super().get()

    @required_master_tenant()
    @required_acl('confd.asterisk.confbridge.wazo_default_user.update')
    def put(self):
        return super().put()
