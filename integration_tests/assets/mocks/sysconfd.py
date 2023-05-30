#!/usr/bin/env python3
# Copyright 2019-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flask import Flask, request, jsonify

logging.basicConfig(level=logging.DEBUG)

_EMPTY_RESPONSES = {
    'get_ha_config': {'node_type': 'disabled', 'remote_address': ''},
}

app = Flask(__name__)

_requests = []
_responses = {}


def _reset():
    global _requests
    global _responses
    _requests = []
    _responses = dict(_EMPTY_RESPONSES)


@app.before_request
def log_request():
    if not request.path.startswith('/_requests'):
        path = request.path
        log = {
            'method': request.method,
            'path': path,
            'query': dict(request.args.items()),
            'body': request.data.decode('utf-8'),
            'json': request.json if request.is_json else None,
            'headers': dict(request.headers),
        }
        _requests.append(log)


@app.route('/_requests', methods=['GET'])
def list_requests():
    return jsonify(requests=_requests)


@app.route('/_reset', methods=['POST'])
def reset():
    _reset()
    return '', 204


@app.route('/_set_response', methods=['POST'])
def set_response():
    global _responses
    request_body = request.json
    set_response = request_body['response']
    set_response_body = request_body['content']
    _responses[set_response] = set_response_body
    logging.debug('_responses: %s', _responses)
    return '', 204


@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def fallback(path):
    global _responses
    logging.info("fallback handler for path: %s", path)
    return _responses.get(path, '')


@app.route('/get_ha_config')
def get_ha_config():
    return jsonify(_responses['get_ha_config'])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8668)
