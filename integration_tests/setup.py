#!/usr/bin/env python3
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup


setup(
    name='wazo_confd_test_helpers',
    version='1.0.0',
    description='Wazo confd test helpers',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    packages=['wazo_confd_test_helpers', 'wazo_confd_test_helpers.helpers'],
    package_dir={
        'wazo_confd_test_helpers': 'suite/helpers',
        'wazo_confd_test_helpers.helpers': 'suite/helpers/helpers',
    },
)
