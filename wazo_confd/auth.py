# Copyright 2014-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo.auth_verifier import required_acl, required_tenant, no_auth
from wazo.rest_api_helpers import APIException
from wazo.status import Status

from werkzeug.local import LocalProxy as Proxy

from .http_server import app


class NotInitializedException(APIException):
    def __init__(self):
        msg = 'wazo-confd is not initialized'
        super().__init__(503, msg, 'not-initialized')


def required_master_tenant():
    return required_tenant(master_tenant_uuid)


def init_master_tenant(token):
    tenant_uuid = token['metadata']['tenant_uuid']
    app.config['auth']['master_tenant_uuid'] = tenant_uuid


def get_master_tenant_uuid():
    if not app:
        raise Exception('Flask application not configured')

    tenant_uuid = app.config['auth'].get('master_tenant_uuid')
    if not tenant_uuid:
        raise NotInitializedException()
    return tenant_uuid


def provide_status(status):
    status['master_tenant']['status'] = (
        Status.ok if app.config['auth'].get('master_tenant_uuid') else Status.fail
    )


master_tenant_uuid = Proxy(get_master_tenant_uuid)
__all__ = ['required_acl', 'no_auth']
