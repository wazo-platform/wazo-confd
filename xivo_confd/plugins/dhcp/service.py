# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_confd.database import dhcp as dhcp_dao


class DHCPService:

    def __init__(self, notifier):
        self.notifier = notifier

    def get(self):
        return dhcp_dao.get()

    def edit(self, form):
        dhcp_dao.update(form)
        self.notifier.edited()
