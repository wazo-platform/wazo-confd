# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(incall_id, extension_id, check=True):
    response = confd.incalls(incall_id).extensions(extension_id).put()
    if check:
        response.assert_ok()


def dissociate(incall_id, extension_id, check=True):
    response = confd.incalls(incall_id).extensions(extension_id).delete()
    if check:
        response.assert_ok()
