# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.dhcp import Dhcp
from xivo_dao.helpers.db_manager import Session


class DHCPService(object):

    def get(self):
        return Session.query(Dhcp).first()

    def edit(self, form):
        dhcp = Session.query(Dhcp).first()
        for name, value in form.iteritems():
            setattr(dhcp, name, value)


def build_service():
    return DHCPService()
