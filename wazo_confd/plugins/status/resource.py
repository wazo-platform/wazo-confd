# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo.auth_verifier import required_acl
from wazo_confd.helpers.restful import ConfdResource


class StatusChecker(ConfdResource):
    def __init__(self, status_aggregator):
        self.status_aggregator = status_aggregator

    @required_acl('confd.status.read')
    def get(self):
        return self.status_aggregator.status(), 200
