# -*- coding: UTF-8 -*-
# Copyright (C) 2012-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
