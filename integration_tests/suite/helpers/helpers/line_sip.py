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


def generate_line_sip(**params):
    line = line_helper.generate_line(**params)
    sip = endpoint_sip.generate_sip(**params)
    line_endpoint_sip.associate(line['id'], sip['id'])
    line_with_sip = confd.lines(line['id']).get().item
    return line_with_sip
