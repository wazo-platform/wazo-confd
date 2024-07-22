# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_test_helpers import until

from ..helpers.wait_strategy import RestAPIOkWaitStrategy
from . import BaseIntegrationTest, confd, confd_with_config


def test_restrict_when_service_token_not_initialized():
    def _returns_503():
        response = confd.extensions.features.get()
        response.assert_status(503)

    config = {'auth': {'username': 'invalid-service'}}
    with confd_with_config(config):
        RestAPIOkWaitStrategy().wait(BaseIntegrationTest)
        until.assert_(_returns_503, tries=10)
