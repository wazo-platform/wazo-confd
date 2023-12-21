# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.line import dao as line_dao_module

from wazo_confd.plugins.line.service import build_service as build_line_service

from .notifier import build_notifier_custom, build_notifier_sccp, build_notifier_sip
from .validator import build_validator_custom, build_validator_sccp, build_validator_sip


class LineEndpointSIPService:
    def __init__(self, line_dao, line_service, validator, notifier):
        self.line_dao = line_dao
        self.line_service = line_service
        self.validator = validator
        self.notifier = notifier

    def associate(self, line, endpoint):
        if line.endpoint_sip_uuid == endpoint.uuid:
            return

        self.validator.validate_association(line, endpoint)
        self.line_dao.associate_endpoint_sip(line, endpoint)
        self.line_service.edit(line, None)
        self.notifier.associated(line, endpoint)

    def dissociate(self, line, endpoint):
        if line.endpoint_sip_uuid != endpoint.uuid:
            return

        self.validator.validate_dissociation(line, endpoint)
        self.line_dao.dissociate_endpoint_sip(line, endpoint)
        self.line_service.edit(line, None)
        self.notifier.dissociated(line, endpoint)


class LineEndpointSCCPService:
    def __init__(self, line_dao, line_service, validator, notifier):
        self.line_dao = line_dao
        self.line_service = line_service
        self.validator = validator
        self.notifier = notifier

    def associate(self, line, endpoint):
        if line.endpoint_sccp_id == endpoint.id:
            return

        self.validator.validate_association(line, endpoint)
        self.line_dao.associate_endpoint_sccp(line, endpoint)
        self.line_service.edit(line, None)
        self.notifier.associated(line, endpoint)

    def dissociate(self, line, endpoint):
        if line.endpoint_sccp_id != endpoint.id:
            return

        self.validator.validate_dissociation(line, endpoint)
        self.line_dao.dissociate_endpoint_sccp(line, endpoint)
        self.line_service.edit(line, None)
        self.notifier.dissociated(line, endpoint)


class LineEndpointCustomService:
    def __init__(self, line_dao, line_service, validator, notifier):
        self.line_dao = line_dao
        self.line_service = line_service
        self.validator = validator
        self.notifier = notifier

    def associate(self, line, endpoint):
        if line.endpoint_custom_id == endpoint.id:
            return

        self.validator.validate_association(line, endpoint)
        self.line_dao.associate_endpoint_custom(line, endpoint)
        self.line_service.edit(line, None)
        self.notifier.associated(line, endpoint)

    def dissociate(self, line, endpoint):
        if line.endpoint_custom_id != endpoint.id:
            return

        self.validator.validate_dissociation(line, endpoint)
        self.line_dao.dissociate_endpoint_custom(line, endpoint)
        self.line_service.edit(line, None)
        self.notifier.dissociated(line, endpoint)


def build_service_sip(provd_client):
    validator = build_validator_sip()
    line_service = build_line_service(provd_client)
    notifier = build_notifier_sip()
    return LineEndpointSIPService(line_dao_module, line_service, validator, notifier)


def build_service_sccp(provd_client):
    validator = build_validator_sccp()
    line_service = build_line_service(provd_client)
    notifier = build_notifier_sccp()
    return LineEndpointSCCPService(line_dao_module, line_service, validator, notifier)


def build_service_custom(provd_client):
    validator = build_validator_custom()
    line_service = build_line_service(provd_client)
    notifier = build_notifier_custom()
    return LineEndpointCustomService(line_dao_module, line_service, validator, notifier)
