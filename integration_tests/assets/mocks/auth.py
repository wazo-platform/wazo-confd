#!/usr/bin/env python3
# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/0.1/token', methods=['POST'])
def list_requests():
    return jsonify({'data': {'token': 'the-token'}})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9497, debug=True)
