# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from xivo_dao import tenant_dao
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao

from .service import DefaultSIPTemplateService
from ..._sysconfd import SysconfdPublisher
from ...sync_db import remove_tenant

logger = logging.getLogger(__name__)


class TenantEventHandler:
    def __init__(self, tenant_dao, service, config):
        self.tenant_dao = tenant_dao
        self.service = service
        self.sysconfd = SysconfdPublisher.from_config(config)

    def subscribe(self, bus_consumer):
        bus_consumer.subscribe('auth_tenant_added', self._auth_tenant_added)
        bus_consumer.subscribe('auth_tenant_deleted', self._auth_tenant_deleted)

    def _auth_tenant_added(self, event):
        tenant_uuid = event['uuid']
        slug = event['slug']
        with session_scope():
            tenant = self.tenant_dao.find_or_create_tenant(tenant_uuid)
            self.service.generate_sip_templates(tenant)
            self.service.copy_slug(tenant, slug)

    def _auth_tenant_deleted(self, event):
        remove_tenant(event['uuid'], self.sysconfd)


class Plugin:
    def load(self, dependencies):
        bus_consumer = dependencies['bus_consumer']
        config = dependencies['config']

        service = DefaultSIPTemplateService(sip_dao, transport_dao)
        tenant_event_handler = TenantEventHandler(
            tenant_dao,
            service,
            config,
        )
        tenant_event_handler.subscribe(bus_consumer)
