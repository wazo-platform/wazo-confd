# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(user_id, funckey_template_id, check=True):
    response = confd.users(user_id).funckeys.templates(funckey_template_id).put()
    if check:
        response.assert_ok()


def dissociate(user_id, funckey_template_id, check=True):
    response = confd.users(user_id).funckeys.templates(funckey_template_id).delete()
    if check:
        response.assert_ok()
