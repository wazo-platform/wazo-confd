# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique
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

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/0.1/tenants/<tenant>/phonebooks', methods=['POST'])
def list_requests(tenant):
    phonebook_body = request.get_json()
    phonebook_body['id'] = 42
    return jsonify(phonebook_body), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9489, debug=True)
