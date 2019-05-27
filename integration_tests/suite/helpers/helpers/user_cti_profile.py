# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(user_id, cti_profile_id, **kwargs):
    check = kwargs.pop('check', True)
    enabled = kwargs.pop('enabled', True)
    response = confd.users(user_id).cti.put(enabled=enabled,
                                            cti_profile_id=cti_profile_id)
    if check:
        response.assert_ok()


def dissociate(user_id, cti_profile_id, **kwargs):
    check = kwargs.pop('check', True)
    enabled = kwargs.pop('enabled', False)
    response = confd.users(user_id).cti.put(enabled=enabled,
                                            cti_profile_id=None)
    if check:
        response.assert_ok()
