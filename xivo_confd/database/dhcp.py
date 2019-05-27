# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.dhcp import Dhcp
from xivo_dao.helpers.db_manager import Session


def get():
    return Session.query(Dhcp).first()


def update(dhcp_form):
    dhcp = Session.query(Dhcp).first()
    for name, value in dhcp_form.items():
        setattr(dhcp, name, value)
