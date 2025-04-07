# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries, is_not, none

from . import confd


def test_get():
    response = confd.infos.get()
    assert_that(
        response.item, has_entries(uuid=is_not(none()), wazo_version=is_not(none()))
    )
