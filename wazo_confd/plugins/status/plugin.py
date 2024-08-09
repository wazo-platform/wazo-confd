# Copyright 2022-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo.status import Status

from .resource import StatusChecker


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        status_aggregator = dependencies['status_aggregator']

        status_aggregator.add_provider(provide_status)

        api.add_resource(
            StatusChecker,
            '/status',
            resource_class_args=[status_aggregator],
        )


def provide_status(status):
    status['rest_api']['status'] = Status.ok
