# Copyright 2020-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from wazo_provd_client import Client as ProvdClient
from xivo_dao import tenant_dao
from xivo_dao.helpers.db_utils import session_scope
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao

from .service import DefaultSIPTemplateService

logger = logging.getLogger(__name__)


class TenantEventHandler:
    def __init__(self, tenant_dao, service, provd_client):
        self.tenant_dao = tenant_dao
        self.service = service
        self.provd = provd_client

    def subscribe(self, bus_consumer):
        bus_consumer.on_event('auth_tenant_added', self._auth_tenant_added)
        bus_consumer.on_event('auth_tenant_deleted', self._auth_tenant_deleted)

    def _auth_tenant_added(self, event):
        tenant_uuid = event['uuid']
        slug = event['slug']
        with session_scope():
            tenant = self.tenant_dao.find_or_create_tenant(tenant_uuid)
            self.service.generate_sip_templates(tenant)
            self.service.copy_slug(tenant, slug)

    def _auth_tenant_deleted(self, event):
        tenant_uuid = event['uuid']
        logger.debug('Deleting devices for tenant "%s"', tenant_uuid)
        devices = self.provd.devices.list(tenant_uuid=tenant_uuid, recurse=True)[
            'devices'
        ]
        for device in devices:
            self.provd.devices.delete(device['id'])


class Plugin:
    def load(self, dependencies):
        config = dependencies['config']
        bus_consumer = dependencies['bus_consumer']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = DefaultSIPTemplateService(sip_dao, transport_dao)
        tenant_event_handler = TenantEventHandler(tenant_dao, service, provd_client)
        tenant_event_handler.subscribe(bus_consumer)
