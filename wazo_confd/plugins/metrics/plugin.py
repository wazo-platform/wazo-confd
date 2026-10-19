# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo.flask.metrics import init_flask_metrics


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']

        init_flask_metrics(api.app, api)
