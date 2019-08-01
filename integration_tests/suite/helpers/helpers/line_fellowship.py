# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager
from .. import helpers as h


@contextmanager
def line_fellowship(endpoint_type='sip', registrar=None, wazo_tenant=None):
    context = h.context.generate_context(wazo_tenant=wazo_tenant)
    user = h.user.generate_user(wazo_tenant=wazo_tenant, context=context['name'])
    line = h.line.generate_line(
        wazo_tenant=wazo_tenant,
        context=context['name'],
        registrar=registrar,
    )
    extension = h.extension.generate_extension(wazo_tenant=wazo_tenant, context=context['name'])

    if endpoint_type == 'sip':
        endpoint = h.endpoint_sip.generate_sip(wazo_tenant=wazo_tenant)
        line_endpoint = h.line_endpoint_sip
    else:
        endpoint = h.endpoint_sccp.generate_sccp(wazo_tenant=wazo_tenant)
        line_endpoint = h.line_endpoint_sccp

    line_endpoint.associate(line['id'], endpoint['id'])
    h.user_line.associate(user['id'], line['id'])
    h.line_extension.associate(line['id'], extension['id'])

    yield user, line, extension, endpoint

    h.line_extension.dissociate(line['id'], extension['id'], False)
    h.user_line.dissociate(user['id'], line['id'], False)
    line_endpoint.dissociate(line['id'], endpoint['id'], False)

    if endpoint_type == 'sip':
        h.endpoint_sip.delete_sip(endpoint['id'])
    else:
        h.endpoint_sccp.delete_sccp(endpoint['id'])

    h.user.delete_user(user['id'])
    h.line.delete_line(line['id'])
    h.extension.delete_extension(extension['id'])
