# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(line_id, extension_id, check=True):
    response = confd.lines(line_id).extensions(extension_id).put()
    if check:
        response.assert_ok()


def dissociate(line_id, extension_id, check=True):
    response = confd.lines(line_id).extensions(extension_id).delete()
    if check:
        response.assert_ok()
