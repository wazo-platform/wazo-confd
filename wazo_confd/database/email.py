# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.mail import Mail
from xivo_dao.helpers.db_manager import Session


def get():
    return Session.query(Mail).first()


def update(email_config):
    Session.add(email_config)
    Session.flush()
