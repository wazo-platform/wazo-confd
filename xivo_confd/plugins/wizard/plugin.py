# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import logging

from xivo_auth_client import Client as AuthClient
from xivo_dird_client import Client as DirdClient

from xivo_confd import api
from xivo_confd.plugins.wizard.service import build_service
from xivo_confd.plugins.wizard.resource import WizardResource, WizardDiscoverResource
from xivo_dao.resources.infos import dao as infos_dao

logger = logging.getLogger(__name__)


class Plugin(object):

    def load(self, core):
        service_id = core.config['wizard']['service_id']
        service_key = core.config['wizard']['service_key']
        if not service_id or not service_key:
            logger.info('failed to load the wizard plugin: missing service_id or service_key')
            return

        auth_client = AuthClient(username=service_id,
                                 password=service_key,
                                 **core.config['auth'])
        dird_client = DirdClient(**core.config['dird'])
        provd_client = core.provd_client()

        service = build_service(provd_client, auth_client, dird_client, infos_dao)

        api.add_resource(WizardResource,
                         '/wizard',
                         endpoint='wizard',
                         resource_class_args=(service,)
                         )

        api.add_resource(WizardDiscoverResource,
                         '/wizard/discover',
                         resource_class_args=(service,)
                         )
