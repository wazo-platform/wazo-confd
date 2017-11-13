# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      has_entries,
                      has_item)

from ..helpers import fixtures
from ..helpers import scenarios as s
from . import confd

FAKE_ID = 999999999


def test_get_errors():
    fake_get = confd.cti_profiles(FAKE_ID).get
    yield s.check_resource_not_found, fake_get, 'CtiProfile'


@fixtures.cti_profile()
def test_list(cti_profile):
    response = confd.cti_profiles.get()
    assert_that(response.items, has_item(has_entries(id=cti_profile['id'],
                                                     name=cti_profile['name'])))


@fixtures.cti_profile()
def test_get(cti_profile):
    response = confd.cti_profiles(cti_profile['id']).get()
    assert_that(response.item, has_entries(id=cti_profile['id'],
                                           name=cti_profile['name']))
