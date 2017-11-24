# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(user_id, cti_profile_id, check=True):
    response = confd.users(user_id).cti.put(enabled=True,
                                            cti_profile_id=cti_profile_id)
    if check:
        response.assert_ok()


def dissociate(user_id, cti_profile_id, check=True):
    response = confd.users(user_id).cti.put(enabled=False,
                                            cti_profile_id=None)
    if check:
        response.assert_ok()
