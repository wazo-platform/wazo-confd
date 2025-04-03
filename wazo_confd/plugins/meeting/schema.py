# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from base64 import b64encode
from marshmallow import fields
from marshmallow.validate import Length

from wazo.rest_api_helpers import APIException

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink

logger = logging.getLogger(__name__)


class NoIngressHTTPException(APIException):
    def __init__(self):
        self.msg = 'no Ingress HTTP configured'
        super().__init__(503, self.msg, 'not-configured')

    def __str__(self):
        return self.msg


class MeetingSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    owner_uuids = fields.List(fields.UUID())
    name = fields.String(validate=Length(max=512), required=True)
    ingress_http_uri = fields.Method('_uri', dump_only=True)
    guest_sip_authorization = fields.Method('_guest_sip_authorization', dump_only=True)
    persistent = fields.Boolean(load_default=False)
    links = ListLink(Link('meetings', field='uuid'))
    tenant_uuid = fields.String(dump_only=True)
    creation_time = fields.DateTime(attribute='created_at', dump_only=True)
    exten = fields.Method('_exten', dump_only=True)
    require_authorization = fields.Boolean(load_default=False)

    def _uri(self, meeting):
        if meeting.ingress_http:
            return meeting.ingress_http.uri

        default_ingress_http = self.context['default_ingress_http']
        if default_ingress_http:
            return default_ingress_http.uri

        raise NoIngressHTTPException()

    def _exten(self, meeting):
        prefix = self.context['exten_prefix']
        if not prefix:
            logger.debug(
                'cannot add the meeting exten, no "meetingjoin" extension_features configured'
            )
            return
        return '{}{}'.format(prefix, meeting.number)

    def _guest_sip_authorization(self, model):
        if not model.guest_endpoint_sip:
            return None

        if model.require_authorization:
            return None

        return self.format_sip_authorization(model.guest_endpoint_sip)

    @staticmethod
    def format_sip_authorization(endpoint_sip):
        username = None
        password = None
        for option, value in endpoint_sip.auth_section_options:
            if option == 'username':
                username = value
            elif option == 'password':
                password = value

        if username is None or password is None:
            return None

        return b64encode('{}:{}'.format(username, password).encode()).decode()
