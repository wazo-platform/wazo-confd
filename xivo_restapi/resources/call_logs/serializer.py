# -*- coding: UTF-8 -*-
#
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import csv
from StringIO import StringIO
from xivo.unicode_csv import UnicodeDictWriter

CSV_HEADERS = ['Call Date',
               'Caller',
               'Called',
               'Period',
               'user Field']


def encode_list(call_logs):
    response = StringIO()
    write_headers(response, CSV_HEADERS)
    write_body(response, CSV_HEADERS, call_logs)
    return response.getvalue()


def write_headers(csv_file, headers):
    writer = csv.writer(csv_file)
    writer.writerow(headers)


def write_body(csv_file, headers, call_logs):
    writer = UnicodeDictWriter(csv_file, CSV_HEADERS)
    for call_log in call_logs:
        writer.writerow(call_log)
