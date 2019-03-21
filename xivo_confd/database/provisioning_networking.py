# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.provisioning import Provisioning
from xivo_dao.helpers.db_manager import Session


def get():
    return Session.query(Provisioning).first()


def update(provisioning_networking):
    Session.add(provisioning_networking)
    Session.flush()
