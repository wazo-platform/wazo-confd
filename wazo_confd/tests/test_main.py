# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest.mock import patch

import pytest
from xivo.config_helper import UUIDNotFound

from ..config import DEFAULT_CONFIG
from ..main import main


@pytest.fixture
def environment():
    with (
        patch('wazo_confd.main.xivo_logging'),
        patch('wazo_confd.main.change_user') as change_user,
        patch('wazo_confd.main.set_xivo_uuid') as set_xivo_uuid,
        patch('wazo_confd.main.Controller') as controller_class,
        patch('wazo_confd.main.load_config') as load_config,
    ):
        load_config.return_value = dict(DEFAULT_CONFIG)
        yield {
            'change_user': change_user,
            'set_xivo_uuid': set_xivo_uuid,
            'controller_class': controller_class,
            'load_config': load_config,
        }


def test_main_runs_the_controller_as_the_configured_user(environment):
    main([])

    environment['change_user'].assert_called_once_with('www-data')
    environment['controller_class'].assert_called_once_with(
        environment['load_config'].return_value
    )
    environment['controller_class'].return_value.run.assert_called_once()


def test_main_runs_without_a_uuid_when_service_discovery_is_disabled(environment):
    environment['set_xivo_uuid'].side_effect = UUIDNotFound

    main([])

    environment['controller_class'].return_value.run.assert_called_once()


def test_main_requires_a_uuid_when_service_discovery_is_enabled(environment):
    environment['set_xivo_uuid'].side_effect = UUIDNotFound
    environment['load_config'].return_value = dict(
        DEFAULT_CONFIG, service_discovery={'enabled': True}
    )

    with pytest.raises(UUIDNotFound):
        main([])

    environment['controller_class'].assert_not_called()
