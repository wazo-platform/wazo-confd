# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_test_helpers import until
from requests.exceptions import ConnectionError

from . import BaseIntegrationTest, confd, auth


def test_restrict_on_with_slow_wazo_auth():
    BaseIntegrationTest.stop_service('confd')
    BaseIntegrationTest.stop_service('auth')
    BaseIntegrationTest.start_service('confd')
    confd._reset()

    def _returns_503():
        try:
            response = confd.extensions.features.get()
            response.assert_status(503)
        except ConnectionError:
            raise AssertionError

    until.assert_(_returns_503, tries=10)

    BaseIntegrationTest.start_service('auth')
    BaseIntegrationTest.setup_token()
    auth._reset()

    def _not_return_503():
        response = confd.extensions.features.get()
        response.assert_status(200)

    until.assert_(_not_return_503, tries=10)
