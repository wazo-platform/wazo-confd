# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd import bus, sysconfd

from .notifier import ProvisioningNetworkingNotifier
from .resource import ProvisioningNetworkingResource
from .service import ProvisioningNetworkingService


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        notifier = ProvisioningNetworkingNotifier(bus, sysconfd)
        service = ProvisioningNetworkingService(notifier, sysconfd)

        api.add_resource(
            ProvisioningNetworkingResource,
            '/provisioning/networking',
            resource_class_args=(service,)
        )
