# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from werkzeug.local import LocalProxy as Proxy
from .http_server import get_bus_publisher
from .http_server import get_sysconfd_publisher

bus = Proxy(get_bus_publisher)
sysconfd = Proxy(get_sysconfd_publisher)
