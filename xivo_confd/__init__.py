# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from werkzeug.local import LocalProxy
from .server import get_bus_publisher
from .server import get_sysconfd_publisher

bus = LocalProxy(get_bus_publisher)
sysconfd = LocalProxy(get_sysconfd_publisher)
