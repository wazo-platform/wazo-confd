# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest.mock import Mock, patch

from ..plugin import Plugin


@patch('wazo_confd.plugins.metrics.plugin.init_flask_metrics')
def test_load_instruments_the_api_app(init_flask_metrics):
    api = Mock()

    Plugin().load({'api': api})

    init_flask_metrics.assert_called_once_with(api.app, api)
