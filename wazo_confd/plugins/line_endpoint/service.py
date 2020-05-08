# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.plugins.line.service import build_service as build_line_service

from .notifier import build_notifier
from .validator import build_validator


class LineEndpointService:
    def __init__(self, endpoint, line_service, validator, notifier):
        self.endpoint = endpoint
        self.line_service = line_service
        self.validator = validator
        self.notifier = notifier

    def associate(self, line, endpoint):
        if line.is_associated_with(endpoint):
            return

        self.validator.validate_association(line, endpoint)
        line.associate_endpoint(endpoint)
        self.line_service.edit(line, None)
        self.notifier.associated(line, endpoint)

    def dissociate(self, line, endpoint):
        if not line.is_associated_with(endpoint):
            return

        self.validator.validate_dissociation(line, endpoint)
        line.remove_endpoint()
        self.line_service.edit(line, None)
        self.notifier.dissociated(line, endpoint)


def build_service(provd_client, endpoint):
    validator = build_validator(endpoint)
    line_service = build_line_service(provd_client)
    notifier = build_notifier(endpoint)
    return LineEndpointService(endpoint, line_service, validator, notifier)
