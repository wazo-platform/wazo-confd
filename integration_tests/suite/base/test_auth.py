# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_test_helpers import until
from requests.exceptions import ConnectionError

from ..helpers.helpers import confd as helper_confd, new_client as helper_new_client
from . import BaseIntegrationTest, confd, confd_csv, auth


def test_restrict_on_with_slow_wazo_auth():
    BaseIntegrationTest.stop_service('confd')
    BaseIntegrationTest.stop_service('auth')
    BaseIntegrationTest.start_service('confd')
    BaseIntegrationTest.setup_helpers()
    helper_confd._reset()
    helper_new_client._reset()
    confd._reset()
    confd_csv._reset()

    def _returns_503():
        try:
            response = confd.extensions.features.get()
            response.assert_status(503)
        except ConnectionError:
            raise AssertionError

    until.assert_(_returns_503, tries=10)

    BaseIntegrationTest.start_service('auth')
    auth._reset()
    until.true(auth.is_up, tries=5)
    BaseIntegrationTest.setup_token()
    BaseIntegrationTest.setup_service_token()

    def _not_return_503():
        response = confd.extensions.features.get()
        response.assert_status(200)

    until.assert_(_not_return_503, tries=10)
