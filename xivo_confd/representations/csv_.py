# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from cStringIO import StringIO
from flask import (
    json,
    make_response,
)
from xivo.unicode_csv import UnicodeDictWriter


def output_csv(data, code, http_headers=None):
    # A 401 might happen when trying to find the tenant if the specified tenant is not authorized
    if code == 401:
        return make_response(json.dumps(data), code)

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
