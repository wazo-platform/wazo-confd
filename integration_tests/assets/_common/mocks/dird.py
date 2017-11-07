# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique
#
# SPDX-License-Identifier: GPL-3.0+

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/0.1/tenants/<tenant>/phonebooks', methods=['POST'])
def list_requests(tenant):
    phonebook_body = request.get_json()
    phonebook_body['id'] = 42
    return jsonify(phonebook_body), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9489, debug=True)
