#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (C) 2012-2015  Avencall
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

from setuptools import setup
from setuptools import find_packages

setup(
    name='xivo-confd',
    version='0.1',
    description='XIVO CONFD daemon',
    author='Avencall',
    author_email='dev@avencall.com',
    url='http://github.com/xivo-pbx/xivo-confd',
    license='GPLv3',
    packages=find_packages(),
    scripts=[
        'bin/xivo-confd'
    ],

    package_data={
        'xivo_confd.resources.api': ['*.json'],
    },

    zip_safe=False,
    entry_points={
        'xivo_confd.plugins': [
            'plugin_list = xivo_confd.plugins.plugin_list:Plugin',
        ]
    }
)
