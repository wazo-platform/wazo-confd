# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd import bus, sysconfd

from .notifier import EmailConfigNotifier
from .resource import EmailConfig
from .service import EmailConfigService


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']

        notifier = EmailConfigNotifier(bus, sysconfd)
        service = EmailConfigService(notifier)

        api.add_resource(EmailConfig, '/emails', resource_class_args=(service,))
