# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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


def build_service(provd_client):
    device_updater = device_builder.build_device_updater(provd_client)

    return SipEndpointService(
        endpoint_sip_dao_module, build_validator(), build_notifier(), device_updater
    )
