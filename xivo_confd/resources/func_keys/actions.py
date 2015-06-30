# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

import logging

from flask import Blueprint

from xivo_dao.resources.bsfilter import dao as bsfilter_dao
from xivo_dao.resources.func_key_template import dao as template_dao
from xivo_dao.resources.user import dao as user_dao

from xivo_confd import config
from xivo_confd.helpers.resource import DecoratorChain, CRUDResource
from xivo_confd.resources.func_keys.resource import FuncKeyResource, UserFuncKeyResource, UserTemplateResource, TemplateManipulator
from xivo_confd.resources.devices import builder as device_builder

from xivo_confd.resources.func_keys import service as fk_service
from xivo_confd.resources.func_keys import converter as fk_converter
from xivo_confd.resources.func_keys import validator as fk_validator
from xivo_confd.resources.func_keys import notifier

logger = logging.getLogger(__name__)


def load(core_rest_api):
    validator = fk_validator.build_validators()
    bsfilter_validator = fk_validator.BSFilterValidator(bsfilter_dao)

    funckey_converter = fk_converter.build_funckey_converter(exclude=['agent', 'bsfilter'])
    user_funckey_converter = fk_converter.build_funckey_converter()

    template_converter = fk_converter.build_template_converter(funckey_converter)
    user_template_converter = fk_converter.build_template_converter(user_funckey_converter)

    provd_client = core_rest_api.provd_client()
    device_dao = device_builder.build_dao(provd_client)
    device_updater = device_builder.build_device_updater(device_dao)

    service = fk_service.TemplateService(validator,
                                         template_dao,
                                         user_dao,
                                         notifier,
                                         device_updater)

    template_manipulator = TemplateManipulator(service, device_updater, user_dao)
    template_resource = CRUDResource(service, template_converter)
    funckey_resource = FuncKeyResource(template_manipulator, funckey_converter)
    user_funckey_resource = UserFuncKeyResource(template_manipulator, user_funckey_converter, bsfilter_validator, user_dao)
    user_template_resource = UserTemplateResource(template_manipulator, user_template_converter)

    blueprint = Blueprint('func_key_templates', __name__, url_prefix='/%s/funckeys/templates' % config.API_VERSION)
    user_blueprint = core_rest_api.blueprint('users')

    chain = DecoratorChain(core_rest_api, blueprint)

    chain.search().decorate(template_resource.search)
    chain.get().decorate(template_resource.get)
    chain.create().decorate(template_resource.create)
    chain.delete().decorate(template_resource.delete)

    chain.edit("/<int:template_id>/<int:position>").decorate(funckey_resource.update_funckey)
    chain.delete("/<int:template_id>/<int:position>").decorate(funckey_resource.remove_funckey)
    chain.get("/<int:template_id>/<int:position>").decorate(funckey_resource.get_funckey)

    user_chain = DecoratorChain(core_rest_api, user_blueprint)

    user_chain.get("/<int:user_id>/funckeys/<int:position>").decorate(user_funckey_resource.get_funckey)
    user_chain.edit("/<int:user_id>/funckeys/<int:position>").decorate(user_funckey_resource.update_funckey)
    user_chain.delete("/<int:user_id>/funckeys/<int:position>").decorate(user_funckey_resource.remove_funckey)

    user_chain.get("/<int:user_id>/funckeys").decorate(user_template_resource.get_unified_template)
    user_chain.edit("/<int:user_id>/funckeys/templates/<int:template_id>").decorate(user_template_resource.associate_template)
    user_chain.delete("/<int:user_id>/funckeys/templates/<int:template_id>").decorate(user_template_resource.dissociate_template)

    core_rest_api.register(blueprint)
    core_rest_api.register(user_blueprint)
