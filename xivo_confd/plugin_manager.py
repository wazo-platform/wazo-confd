# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging

from stevedore.enabled import EnabledExtensionManager

logger = logging.getLogger(__name__)


def load_plugins(core):
    enabled_plugins = core.config['enabled_plugins']
    logger.debug('Enabled plugins: %s', enabled_plugins)
    plugins = EnabledExtensionManager(namespace='xivo_confd.plugins',
                                      check_func=lambda p: p.name in enabled_plugins,
                                      on_load_failure_callback=plugins_load_fail,
                                      propagate_map_exceptions=True,
                                      invoke_on_load=True)

    try:
        plugins.map(launch_plugin, core)
    except RuntimeError as e:
        logger.error("Could not load enabled plugins")
        logger.exception(e)


def launch_plugin(ext, core):
    logger.debug('Loading dynamic plugin: %s', ext.name)
    ext.obj.load(core)


def plugins_load_fail(_, entrypoint, exception):
    logger.warning("There is an error with this module: %s", entrypoint)
    logger.warning('%s', exception)
