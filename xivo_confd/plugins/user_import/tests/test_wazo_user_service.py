# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import (
    assert_that,
    contains,
    has_entries,
    has_items,
)
from mock import (
    Mock,
    sentinel as s,
)

from ..wazo_user_service import WazoUserService


class TestWazoUserService(unittest.TestCase):

    def setUp(self):
        self.auth_client = Mock()
        self.service = WazoUserService(self.auth_client)

    def test_that_the_tenant_is_used_on_create_when_defined(self):
        user = {
            'tenant_uuid': s.tenant_uuid,
        }

        self.service.create(user)

        assert_that(self.auth_client.new_user.call_args_list, contains(has_items(
            has_entries(tenant_uuid=s.tenant_uuid),
        )))

    def test_that_a_missing_tenant_uuid_does_not_raise(self):
        user = {}

        self.service.create(user)

        assert_that(self.auth_client.new_user.call_args_list, contains(has_items(
            has_entries(tenant_uuid=None),
        )))
