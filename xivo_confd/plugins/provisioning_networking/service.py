# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_confd.database import provisioning_networking as provisioning_networking_dao


class ProvisioningNetworkingService(object):

    def __init__(self, notifier, sysconfd):
        self.notifier = notifier
        self.sysconfd = sysconfd

    def get(self):
        return provisioning_networking_dao.get()

    def edit(self, resource):
        provisioning_networking_dao.update(resource)
        self.notifier.edited(resource)
