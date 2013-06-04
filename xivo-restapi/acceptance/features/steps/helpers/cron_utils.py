# -*- coding: UTF-8 -*-
# Copyright (C) 2012  Avencall
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

import os


def create_dir(dirname):
    dirname = dirname.rstrip("/")
    exists = os.path.exists(dirname)
    list_dirs = []
    head = dirname
    while not exists:
        (head, tail) = os.path.split(head)
        list_dirs.append(tail)
        exists = os.path.exists(head)
    if len(list_dirs) > 0:
        list_dirs.reverse()
        for folder in list_dirs:
            head += "/" + folder
            os.mkdir(head)
