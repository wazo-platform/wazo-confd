# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_items, not_
from . import confd


def test_get():
    response = confd.timezones.get()
    response.assert_ok()

    assert_that(response.items, has_items({'zone_name': 'America/Montreal'}))
    assert_that(response.total, not_(0))
