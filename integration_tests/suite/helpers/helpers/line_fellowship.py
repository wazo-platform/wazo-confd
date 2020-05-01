# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager
from .. import helpers as h
from .. import scenarios as s


@contextmanager
def line_fellowship(
    endpoint_type='sip',
    registrar=None,
    wazo_tenant=None,
    generate_username_password=False,
):
    context = h.context.generate_context(wazo_tenant=wazo_tenant)
    user = h.user.generate_user(wazo_tenant=wazo_tenant, context=context['name'])
    line = h.line.generate_line(
        wazo_tenant=wazo_tenant, context=context['name'], registrar=registrar
    )
    extension = h.extension.generate_extension(
        wazo_tenant=wazo_tenant, context=context['name']
    )

    if endpoint_type == 'sip':
        options = {}
        if generate_username_password:
            options['auth_section_options'] = [
                ['username', s.random_string(8)],
                ['password', s.random_string(8)],
            ]
        endpoint = h.endpoint_sip.generate_sip(wazo_tenant=wazo_tenant, **options)
        line_endpoint = h.line_endpoint_sip
        endpoint_id = endpoint['uuid']
    else:
        endpoint = h.endpoint_sccp.generate_sccp(wazo_tenant=wazo_tenant)
        line_endpoint = h.line_endpoint_sccp
        endpoint_id = endpoint['id']

    line_endpoint.associate(line['id'], endpoint_id)
    h.user_line.associate(user['id'], line['id'])
    h.line_extension.associate(line['id'], extension['id'])

    yield user, line, extension, endpoint

    h.line_extension.dissociate(line['id'], extension['id'], False)
    h.user_line.dissociate(user['id'], line['id'], False)
    line_endpoint.dissociate(line['id'], endpoint_id, False)

    if endpoint_type == 'sip':
        h.endpoint_sip.delete_sip(endpoint_id)
    else:
        h.endpoint_sccp.delete_sccp(endpoint_id)

    h.user.delete_user(user['id'])
    h.line.delete_line(line['id'])
    h.extension.delete_extension(extension['id'])
