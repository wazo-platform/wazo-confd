# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from xivo_dao.resources.endpoint_sip import dao as endpoint_sip_dao_module

from wazo_confd.plugins.device import builder as device_builder
from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator


class SipEndpointService(CRUDService):
    def __init__(self, dao, validator, notifier, device_updater):
        super().__init__(dao, validator, notifier)
        self.device_updater = device_updater

    def edit(self, sip, updated_fields=None):
        super().edit(sip, updated_fields)
        self.device_updater.update_for_endpoint_sip(sip)

    def fetch_relations(self, form):
        form['parents'] = self._get_parents(form['parents'], form['tenant_uuid'])
        return form

    def _get_parents(self, parents, tenant_uuid):
        models = []

        for parent in parents:
            try:
                model = self.dao.get(parent['uuid'], tenant_uuids=[tenant_uuid])
                models.append(model)
            except NotFoundError:
                metadata = {'parents': parent}
                raise errors.param_not_found('parents', 'endpoint_sip', **metadata)

        return models


def build_service(provd_client):
    device_updater = device_builder.build_device_updater(provd_client)

    return SipEndpointService(
        endpoint_sip_dao_module, build_validator(), build_notifier(), device_updater
    )
