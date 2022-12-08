# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors


class UnallocatedDeviceMiddleWare:
    def __init__(self, service):
        self._service = service

    def assign_tenant(self, device_id, tenant_uuid):
        device = self._service.get(device_id)
        if not device.is_new:
            raise errors.not_found('Device', id=device_id)
        self._service.assign_tenant(device, tenant_uuid=tenant_uuid)

    def reset_autoprov(self, device_id, tenant_uuid):
        device = self._service.get(device_id, tenant_uuid=tenant_uuid)
        self._service.reset_autoprov(device, tenant_uuid=tenant_uuid)
