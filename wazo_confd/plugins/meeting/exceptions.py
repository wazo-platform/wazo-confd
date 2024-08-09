# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo.rest_api_helpers import APIException


class MeetingGuestSIPTemplateNotFound(APIException):
    def __init__(self, tenant_uuid):
        self.msg = (
            f'Could not find SIP template for meeting guests in tenant {tenant_uuid}'
        )
        details = {
            'tenant_uuid': tenant_uuid,
        }
        super().__init__(
            503,
            self.msg,
            'meeting-guest-sip-template-not-found',
            details=details,
            resource='meeting',
        )

    def __str__(self):
        return self.msg
