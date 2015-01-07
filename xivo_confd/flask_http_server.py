# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import logging

import pkg_resources

from xivo_confd import config

from xivo_confd.helpers.mooltiparse import parser as mooltiparse_parser


logger = logging.getLogger(__name__)

content_parser = mooltiparse_parser()


def register_blueprints_v1_1(app):
    _load_resources(app)


def _load_resources(app):
    resources = _list_resources()
    for resource in resources:
        pkg_resource = '%s.%s' % (config.RESOURCES_PACKAGE, resource)
        _load_module('%s.routes' % pkg_resource, app)


def _list_resources():
    try:
        contents = sorted(pkg_resources.resource_listdir(config.RESOURCES_PACKAGE, ""))
    except ImportError:
        return []
    resources = []
    for entry in contents:
        if not entry.endswith('.py') and not entry.endswith('.pyc'):
            if pkg_resources.resource_isdir(config.RESOURCES_PACKAGE, entry):
                logger.debug('Resources found: %s', entry)
                resources.append(entry)
    return resources


def _load_module(name, app):
    try:
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
    except ImportError as e:
        logger.error('Module not found %s', name)
        logger.exception(e)
    else:
        mod.register_blueprints(app)
        logger.debug('Module successfully loaded: %s', name)
