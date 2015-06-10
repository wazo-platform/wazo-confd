# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, current_app


blueprint = Blueprint('example', __name__)


class Plugin(object):

    def load(self, app, config):
        app.config['enabled_plugins'] = config['enabled_plugins']
        app.register_blueprint(blueprint)


@blueprint.route('/plugins')
def index():
    plugins = current_app.config['enabled_plugins']
    return jsonify({'data': {'plugin': plugins}})
