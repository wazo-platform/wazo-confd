# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.plugins.line.service import build_service as build_line_service

from .validator import build_validator


class LineEndpointService(object):

    def __init__(self, endpoint, line_service, endpoint_service, validator):
        self.endpoint = endpoint
        self.line_service = line_service
        self.endpoint_service = endpoint_service
        self.validator = validator

    def get_association_from_line(self, line_id):
        line = self.line_service.get(line_id)
        if not line.is_associated(self.endpoint):
            raise errors.not_found('LineEndpoint', line_id=line_id)

        return {'line_id': line.id,
                'endpoint': self.endpoint,
                'endpoint_id': line.endpoint_id}

    def get_association_from_endpoint(self, endpoint_id):
        endpoint = self.endpoint_service.get(endpoint_id)
        line = self.line_service.find_by(protocol=self.endpoint, protocolid=endpoint.id)
        if not line:
            raise errors.not_found('LineEndpoint', endpoint_id=endpoint_id)

        return {'line_id': line.id,
                'endpoint': self.endpoint,
                'endpoint_id': line.endpoint_id}

    def associate(self, line, endpoint):
        if line.is_associated_with(endpoint):
            return

        self.validator.validate_association(line, endpoint)
        line.associate_endpoint(endpoint)
        self.line_service.edit(line, None)

    def dissociate(self, line, endpoint):
        if not line.is_associated_with(endpoint):
            return

        self.validator.validate_dissociation(line, endpoint)
        line.remove_endpoint()
        self.line_service.edit(line, None)


def build_service(provd_client, endpoint, endpoint_service):
    validator = build_validator(endpoint)
    line_service = build_line_service(provd_client)
    return LineEndpointService(endpoint, line_service, endpoint_service, validator)
