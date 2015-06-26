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

from xivo_dao.resources.agent import dao as agent_dao
from xivo_dao.resources.bsfilter import dao as bsfilter_dao
from xivo_dao.resources.conference import dao as conference_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.features import dao as feature_dao
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.paging import dao as paging_dao
from xivo_dao.resources.queue import dao as queue_dao
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.func_key_template import dao as template_dao

from xivo_confd import config
from xivo_confd.helpers.converter import Converter, ResourceSerializer
from xivo_confd.helpers.resource import DecoratorChain, CRUDResource
from xivo_confd.helpers import validator as common_validator
from xivo_confd.resources.func_keys.resource import FuncKeyResource, UserFuncKeyResource, UserTemplateResource
from xivo_confd.resources.devices import builder

from xivo_confd.resources.func_keys import service as fk_service
from xivo_confd.resources.func_keys import converter as fk_converter
from xivo_confd.resources.func_keys import validator as fk_validator
from xivo_confd.resources.func_keys import notifier

logger = logging.getLogger(__name__)


def load(core_rest_api):
    destination_builders = {'user': fk_converter.UserDestinationBuilder(),
                            'group': fk_converter.GroupDestinationBuilder(),
                            'queue': fk_converter.QueueDestinationBuilder(),
                            'conference': fk_converter.ConferenceDestinationBuilder(),
                            'paging': fk_converter.PagingDestinationBuilder(),
                            'service': fk_converter.ServiceDestinationBuilder(),
                            'custom': fk_converter.CustomDestinationBuilder(),
                            'forward': fk_converter.ForwardDestinationBuilder(),
                            'transfer': fk_converter.TransferDestinationBuilder(),
                            'park_position': fk_converter.ParkPositionDestinationBuilder(),
                            'parking': fk_converter.ParkingDestinationBuilder(),
                            'bsfilter': fk_converter.BSFilterDestinationBuilder(),
                            'agent': fk_converter.AgentDestinationBuilder(),
                            }

    template_converter = build_template_converter(destination_builders, {'func_key_templates': 'id'})
    user_template_converter = build_template_converter(destination_builders, {})
    funckey_converter = build_fk_converter(destination_builders)

    validator = build_validator()

    provd_client = core_rest_api.provd_client()
    provd_dao = builder.build_provd_dao(provd_client)
    device_dao = builder.build_dao(provd_client, provd_dao)
    device_updater = builder.build_device_updater(device_dao)

    service = fk_service.TemplateService(validator,
                                         template_dao,
                                         user_dao,
                                         notifier,
                                         device_updater)

    template_resource = CRUDResource(service, template_converter)
    funckey_resource = FuncKeyResource(service, funckey_converter)
    user_funckey_resource = UserFuncKeyResource(funckey_resource, user_dao)
    user_template_resource = UserTemplateResource(user_dao, template_dao, user_template_converter)

    blueprint = Blueprint('func_key_templates', __name__, url_prefix='/%s/funckeys/templates' % config.API_VERSION)
    user_blueprint = core_rest_api.blueprint('users')

    chain = DecoratorChain(core_rest_api, blueprint)

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


def build_fk_converter(destination_builders):
    parser = fk_converter.JsonParser()
    funckey_validator = fk_converter.FuncKeyValidator(destination_builders)
    funckey_mapper = fk_converter.FuncKeyMapper(destination_builders)
    funckey_builder = fk_converter.FuncKeyBuilder(funckey_validator, destination_builders)
    serializer = ResourceSerializer({})
    return Converter(parser, funckey_mapper, serializer, funckey_builder)


def build_template_converter(destination_builders, resources):
    parser = fk_converter.JsonParser()

    funckey_validator = fk_converter.FuncKeyValidator(destination_builders)
    template_validator = fk_converter.TemplateValidator(funckey_validator)

    funckey_mapper = fk_converter.FuncKeyMapper(destination_builders)
    template_mapper = fk_converter.TemplateMapper(funckey_mapper)

    funckey_builder = fk_converter.FuncKeyBuilder(funckey_validator, destination_builders)
    template_builder = fk_converter.TemplateBuilder(template_validator, funckey_builder)

    serializer = ResourceSerializer(resources)

    converter = Converter(parser, template_mapper, serializer, template_builder)

    return converter


def build_validator():
    destination_validators = {
        'user': [common_validator.ResourceGetValidator('user_id', user_dao.get, 'User')],
        'group': [common_validator.ResourceExistValidator('group_id', group_dao.exists, 'Group')],
        'queue': [common_validator.ResourceExistValidator('queue_id', queue_dao.exists, 'Queue')],
        'conference': [common_validator.ResourceExistValidator('conference_id', conference_dao.exists, 'Conference')],
        'custom': [],
        'service': [fk_validator.ServiceValidator(extension_dao)],
        'forward': [fk_validator.ForwardValidator(extension_dao)],
        'transfer': [fk_validator.TransferValidator(feature_dao)],
        'agent': [fk_validator.AgentActionValidator(extension_dao),
                  common_validator.ResourceExistValidator('agent_id', agent_dao.exists, 'Agent')],
        'park_position': [fk_validator.ParkPositionValidator(feature_dao)],
        'parking': [],
        'paging': [common_validator.ResourceExistValidator('paging_id', paging_dao.exists, 'Paging')],
        'bsfilter': [common_validator.ResourceExistValidator('filter_member_id', bsfilter_dao.filter_member_exists, 'FilterMember')],
    }

    funckey_validator = fk_validator.FuncKeyValidator(destination_validators)
    mapping_validator = fk_validator.FuncKeyMappingValidator(funckey_validator)

    required_validator = common_validator.RequiredValidator()
    private_template_validator = fk_validator.PrivateTemplateValidator()

    return common_validator.ValidationGroup(common=[required_validator, mapping_validator],
                                            delete=[private_template_validator])
