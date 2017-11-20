# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from cStringIO import StringIO
from flask import make_response
from xivo.unicode_csv import UnicodeDictWriter


def output_csv(data, code, http_headers=None):
    csv_headers = data['headers']
    csv_entries = data['content']

    csv_text = StringIO()
    writer = UnicodeDictWriter(csv_text, csv_headers)
    writer.writeheader()

    for entry in csv_entries:
        writer.writerow(entry)

    response = make_response(csv_text.getvalue(), code)
    response.headers.extend(http_headers or {})
    return response
