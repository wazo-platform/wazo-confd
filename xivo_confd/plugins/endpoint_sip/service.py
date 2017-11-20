# -*- coding: UTF-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.plugins.device import builder as device_builder

from xivo_dao.resources.endpoint_sip import dao

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.plugins.endpoint_sip.validator import build_validator
from xivo_confd.plugins.endpoint_sip.notifier import build_notifier


class SipEndpointService(CRUDService):

    def __init__(self, dao, validator, notifier, device_updater):
        super(SipEndpointService, self).__init__(dao, validator, notifier)
        self.device_updater = device_updater

    def edit(self, sip, updated_fields=None):
        super(SipEndpointService, self).edit(sip, updated_fields)
        self.device_updater.update_for_endpoint_sip(sip)


def build_service(provd_client):
    device_updater = device_builder.build_device_updater(provd_client)

    return SipEndpointService(dao,
                              build_validator(),
                              build_notifier(),
                              device_updater)
