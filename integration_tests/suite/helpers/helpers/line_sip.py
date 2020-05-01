# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import (
    confd,
    endpoint_sip,
    line as line_helper,
    line_endpoint_sip,
)


def delete_line_sip(line_id, check=False):
    line_helper.delete_line(line_id, check=check)
    # endpoint is deleted by line


def generate_line_sip(context=None, **params):
    # generate_line wants a context name in "context"
    # generate_sip wants a context body in "context" {"uuid": "<UUID>"}
    line_params = dict(params)
    sip_params = dict(params)
    if context:
        line_params['context'] = context['name']
        sip_params['context'] = context

    line = line_helper.generate_line(**line_params)
    sip = endpoint_sip.generate_sip(**sip_params)
    line_endpoint_sip.associate(line['id'], sip['uuid'])
    line_with_sip = confd.lines(line['id']).get().item
    return line_with_sip
