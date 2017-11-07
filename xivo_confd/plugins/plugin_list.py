# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from flask import Blueprint, jsonify, current_app


blueprint = Blueprint('example', __name__)


class Plugin(object):

    def load(self, core):
        app = core.app
        app.config['enabled_plugins'] = core.config['enabled_plugins']
        app.register_blueprint(blueprint)


@blueprint.route('/plugins')
def index():
    plugins = current_app.config['enabled_plugins']
    return jsonify({'data': {'plugin': plugins}})
