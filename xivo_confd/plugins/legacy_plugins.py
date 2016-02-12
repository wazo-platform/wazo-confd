# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from xivo_confd.resources.api import actions as api_actions
from xivo_confd.resources.call_logs import actions as call_logs_actions
from xivo_confd.resources.configuration import actions as configuration_actions
from xivo_confd.resources.cti_profiles import actions as cti_profiles_actions
from xivo_confd.resources.extensions import actions as extensions_actions
from xivo_confd.resources.infos import actions as infos_actions
from xivo_confd.resources.queue_members import actions as queue_members_actions
from xivo_confd.resources.voicemails import actions as voicemails_actions
from xivo_confd.resources.func_keys import actions as func_keys_actions

logger = logging.getLogger(__name__)


class LegacyPlugins(object):

    def load(self, core):
        self.load_resource(api_actions, core)
        self.load_resource(call_logs_actions, core)
        self.load_resource(configuration_actions, core)
        self.load_resource(cti_profiles_actions, core)
        self.load_resource(extensions_actions, core)
        self.load_resource(infos_actions, core)
        self.load_resource(queue_members_actions, core)
        self.load_resource(voicemails_actions, core)
        self.load_resource(func_keys_actions, core)

    def load_resource(self, module, core):
        logger.info("Loading legacy plugin: %s", module.__name__)
        module.load(core)
