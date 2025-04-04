# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from werkzeug.local import LocalProxy as Proxy

from .http_server import get_bus_publisher, get_sysconfd_publisher

bus = Proxy(get_bus_publisher)
sysconfd = Proxy(get_sysconfd_publisher)
