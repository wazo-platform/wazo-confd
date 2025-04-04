# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.endpoint_sip import dao as endpoint_sip_dao_module

from wazo_confd.helpers.resource import CRUDService
from wazo_confd.plugins.device import builder as device_builder

from .notifier import build_endpoint_notifier, build_template_notifier
from .validator import build_validator


class SipEndpointService(CRUDService):
    def __init__(self, dao, validator, notifier, device_updater, template):
        super().__init__(dao, validator, notifier)
        self.device_updater = device_updater
        self.template = template

    def edit(self, sip, updated_fields=None):
        super().edit(sip, updated_fields)
        self.device_updater.update_for_endpoint_sip(sip)

    def search(self, parameters, tenant_uuids=None):
        parameters['template'] = self.template
        return self.dao.search(tenant_uuids=tenant_uuids, **parameters)

    def get(self, resource_id, **kwargs):
        kwargs['template'] = self.template
        return self.dao.get(resource_id, **kwargs)

    def find_by(self, **criteria):
        criteria['template'] = self.template
        return self.dao.find_by(**criteria)

    def get_by(self, **criteria):
        criteria['template'] = self.template
        return self.dao.get_by(**criteria)

    def create(self, resource):
        self.validator.validate_create(resource)
        resource.template = self.template
        created_resource = self.dao.create(resource)
        self.notifier.created(created_resource)
        return created_resource

    def delete(self, resource):
        self.validator.validate_delete(resource)
        self.dao.delete(resource)
        self.notifier.deleted(resource)


def build_endpoint_service(provd_client, pjsip_doc):
    device_updater = device_builder.build_device_updater(provd_client)

    return SipEndpointService(
        endpoint_sip_dao_module,
        build_validator(pjsip_doc),
        build_endpoint_notifier(),
        device_updater,
        template=False,
    )


def build_template_service(provd_client, pjsip_doc):
    device_updater = device_builder.build_device_updater(provd_client)

    return SipEndpointService(
        endpoint_sip_dao_module,
        build_validator(pjsip_doc),
        build_template_notifier(),
        device_updater,
        template=True,
    )
