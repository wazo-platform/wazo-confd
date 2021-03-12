# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.database import email as email_dao


class EmailConfigService:
    def __init__(self, notifier):
        self.notifier = notifier

    def get(self):
        return email_dao.get()

    def edit(self, resource):
        email_dao.update(resource)
        self.notifier.edited()
