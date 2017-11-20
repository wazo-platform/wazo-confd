# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from werkzeug.local import LocalProxy
from xivo_confd.application import app
from xivo_confd.application import api
from xivo_confd.application import auth
from xivo_confd.application import setup_app
from xivo_confd.application import get_bus_publisher
from xivo_confd.application import get_sysconfd_publisher

bus = LocalProxy(get_bus_publisher)
sysconfd = LocalProxy(get_sysconfd_publisher)
