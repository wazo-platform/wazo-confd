# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.line import dao as line_dao_module

from .notifier import (
    build_notifier_sip,
    build_notifier_sccp,
    build_notifier_custom,
)
from .validator import (
    build_validator_sip,
    build_validator_sccp,
    build_validator_custom,
)


class LineEndpointSIPService:
    def __init__(self, line_dao, validator, notifier):
        self.line_dao = line_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, line, endpoint):
        if line.endpoint_sip_uuid == endpoint.uuid:
            return

        self.validator.validate_association(line, endpoint)
        self.line_dao.associate_endpoint_sip(line, endpoint)
        self.line_dao.edit(line)
        self.notifier.associated(line, endpoint)

    def dissociate(self, line, endpoint):
        if line.endpoint_sip_uuid != endpoint.uuid:
            return

        self.validator.validate_dissociation(line, endpoint)
        self.line_dao.dissociate_endpoint_sip(line, endpoint)
        self.line_dao.edit(line)
        self.notifier.dissociated(line, endpoint)


class LineEndpointSCCPService:
    def __init__(self, line_dao, validator, notifier):
        self.line_dao = line_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, line, endpoint):
        if line.endpoint_sccp_id == endpoint.id:
            return

        self.validator.validate_association(line, endpoint)
        self.line_dao.associate_endpoint_sccp(line, endpoint)
        self.line_dao.edit(line)
        self.notifier.associated(line, endpoint)

    def dissociate(self, line, endpoint):
        if line.endpoint_sccp_id != endpoint.id:
            return

        self.validator.validate_dissociation(line, endpoint)
        self.line_dao.dissociate_endpoint_sccp(line, endpoint)
        self.line_dao.edit(line)
        self.notifier.dissociated(line, endpoint)


class LineEndpointCustomService:
    def __init__(self, line_dao, validator, notifier):
        self.line_dao = line_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, line, endpoint):
        if line.endpoint_custom_id == endpoint.id:
            return

        self.validator.validate_association(line, endpoint)
        self.line_dao.associate_endpoint_custom(line, endpoint)
        self.line_dao.edit(line)
        self.notifier.associated(line, endpoint)

    def dissociate(self, line, endpoint):
        if line.endpoint_custom_id != endpoint.id:
            return

        self.validator.validate_dissociation(line, endpoint)
        self.line_dao.dissociate_endpoint_custom(line, endpoint)
        self.line_dao.edit(line)
        self.notifier.dissociated(line, endpoint)


def build_service_sip(provd_client):
    validator = build_validator_sip()
    notifier = build_notifier_sip()
    return LineEndpointSIPService(line_dao_module, validator, notifier)


def build_service_sccp(provd_client):
    validator = build_validator_sccp()
    notifier = build_notifier_sccp()
    return LineEndpointSCCPService(line_dao_module, validator, notifier)


def build_service_custom(provd_client):
    validator = build_validator_custom()
    notifier = build_notifier_custom()
    return LineEndpointCustomService(line_dao_module, validator, notifier)
