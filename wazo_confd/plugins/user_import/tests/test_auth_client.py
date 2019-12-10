# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest import TestCase
from unittest.mock import Mock, sentinel as s
from requests import HTTPError
from hamcrest import (
    assert_that,
    calling,
    raises,
)

from xivo_dao.helpers.exception import ServiceError

from ..auth_client import AuthClientProxy as Client


class TestRollback(TestCase):
    def setUp(self):
        self.auth_client = Mock()
        self.client = Client(self.auth_client)

    def test_that_an_error_in_auth_will_raise_a_service_error(self):
        self.auth_client.users.new.side_effect = HTTPError()

        assert_that(
            calling(self.client.new_user), raises(ServiceError),
        )

    def test_that_rollback_deletes_created_users(self):
        self.auth_client.users.new.return_value = {'uuid': s.user_uuid}

        self.client.new_user(uuid=s.user_uuid)

        self.client.rollback()

        self.auth_client.users.delete.assert_called_once_with(s.user_uuid)
