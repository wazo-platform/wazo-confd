# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(trunk_id, register_id, check=True):
    response = confd.trunks(trunk_id).registers.iax(register_id).put()
    if check:
        response.assert_ok()


def dissociate(trunk_id, register_id, check=True):
    response = confd.trunks(trunk_id).registers.iax(register_id).delete()
    if check:
        response.assert_ok()
