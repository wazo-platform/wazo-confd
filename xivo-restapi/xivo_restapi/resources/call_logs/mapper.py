# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import csv
import logging
from StringIO import StringIO


logger = logging.getLogger(__name__)


def encode_list(calls):
    encoded_data = StringIO()
    csv_writer = csv.writer(encoded_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    headers = ['date', 'source', 'destination', 'duration', 'user_field']
    csv_writer.writerow(headers)

    for call in calls:
        row = [call.date,
               call.source.encode("utf-8"),
               call.destination.encode("utf-8"),
               call.duration,
               call.user_field.encode("utf-8")]
        csv_writer.writerow(row)
    return encoded_data.getvalue()
