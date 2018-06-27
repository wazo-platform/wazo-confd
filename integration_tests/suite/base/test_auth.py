# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import BaseIntegrationTest


def test_ignore_x_forwarded_for_header():
    confd = BaseIntegrationTest.new_client(headers={'X-Forwarded-For': '127.0.0.1'}).url
    response = confd.users.get()
    response.assert_status(401)
