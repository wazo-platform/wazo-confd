# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(group_uuid, extension_id, check=True):
    response = confd.groups(group_uuid).extensions(extension_id).put()
    if check:
        response.assert_ok()


def dissociate(group_uuid, extension_id, check=True):
    response = confd.groups(group_uuid).extensions(extension_id).delete()
    if check:
        response.assert_ok()
