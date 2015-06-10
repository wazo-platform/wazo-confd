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

from stevedore.enabled import EnabledExtensionManager


def load_plugins(application):
    plugins = EnabledExtensionManager(namespace='xivo_confd.plugins',
                                      check_func=check_plugin,
                                      on_load_failure_callback=plugins_load_fail,
                                      propagate_map_exceptions=True,
                                      invoke_on_load=True)

    try:
        plugins.map(launch_plugin, application)
    except RuntimeError:
        print "There is no plugin to load!"


def check_plugin(plugin):
    return True


def launch_plugin(ext, application):
    print "Loading dynamic plugin : %s" % ext.name
    ext.obj.load(application)


def plugins_load_fail(manager, entrypoint, exception):
    print "There is an error with this module: ", manager
    print "The entry point is: ", entrypoint
    print "The exception is: ", exception
