# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.restful import ConfdResource

from .schema import ConfigHistoryDiffSchema, ConfigHistorySchema


class ConfigHistoryResource(ConfdResource):
    schema = ConfigHistorySchema

    def __init__(self, service):
        self.service = service

    @required_master_tenant()
    @required_acl('confd.config_history.read')
    def get(self):
        model = self.service.get_history()
        return self.schema().dump({'items': model})


class ConfigHistoryDiffResource(ConfdResource):
    schema = ConfigHistoryDiffSchema

    def __init__(self, service):
        self.service = service

    @required_master_tenant()
    @required_acl('confd.config_history.diff.read')
    def get(self):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        commit_a = request.args.get('commit_a')
        commit_b = request.args.get('commit_b')
        model = self.service.get_diff(start_date, end_date, commit_a, commit_b)
        return self.schema().dump({'item': model})
