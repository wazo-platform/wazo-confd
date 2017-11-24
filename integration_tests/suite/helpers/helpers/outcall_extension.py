# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(outcall_id, extension_id, **kwargs):
    check = kwargs.pop('check', True)
    response = confd.outcalls(outcall_id).extensions(extension_id).put(**kwargs)
    if check:
        response.assert_ok()


def dissociate(outcall_id, extension_id, **kwargs):
    check = kwargs.get('check', True)
    response = confd.outcalls(outcall_id).extensions(extension_id).delete()
    if check:
        response.assert_ok()
