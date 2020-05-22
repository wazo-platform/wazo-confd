# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo_dao.alchemy.func_key_dest_agent import FuncKeyDestAgent
from xivo_dao.alchemy.func_key_dest_bsfilter import FuncKeyDestBSFilter
from xivo_dao.alchemy.func_key_dest_custom import FuncKeyDestCustom
from xivo_dao.alchemy.func_key_dest_conference import FuncKeyDestConference
from xivo_dao.alchemy.func_key_dest_features import (
    FuncKeyDestTransfer,
    FuncKeyDestOnlineRecording,
    FuncKeyDestParking,
)
from xivo_dao.alchemy.func_key_dest_forward import FuncKeyDestForward
from xivo_dao.alchemy.func_key_dest_group import FuncKeyDestGroup
from xivo_dao.alchemy.func_key_dest_group_member import FuncKeyDestGroupMember
from xivo_dao.alchemy.func_key_dest_paging import FuncKeyDestPaging
from xivo_dao.alchemy.func_key_dest_park_position import FuncKeyDestParkPosition
from xivo_dao.alchemy.func_key_dest_queue import FuncKeyDestQueue
from xivo_dao.alchemy.func_key_dest_service import FuncKeyDestService
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource, ConfdResource

from .schema import (
    FuncKeyDestinationField,
    FuncKeySchema,
    FuncKeyTemplateSchema,
    FuncKeyTemplateUserSchema,
    FuncKeyUnifiedTemplateSchema,
)

models_destination = {
    'agent': FuncKeyDestAgent,
    'bsfilter': FuncKeyDestBSFilter,
    'conference': FuncKeyDestConference,
    'custom': FuncKeyDestCustom,
    'forward': FuncKeyDestForward,
    'group': FuncKeyDestGroup,
    'groupmember': FuncKeyDestGroupMember,
    'onlinerec': FuncKeyDestOnlineRecording,
    'paging': FuncKeyDestPaging,
    'park_position': FuncKeyDestParkPosition,
    'parking': FuncKeyDestParking,
    'queue': FuncKeyDestQueue,
    'service': FuncKeyDestService,
    'transfer': FuncKeyDestTransfer,
    'user': FuncKeyDestUser,
}


def _create_funckey_model(funckey):
    type_ = funckey['destination'].pop('type')
    funckey['destination'] = models_destination[type_](**funckey['destination'])
    return FuncKeyMapping(**funckey)


class FindUpdateFieldsMixin:
    def find_updated_fields_position(self, model, form):
        updated_fields = []
        for position, funckey in form.items():
            funckey_model = model.get(position, FuncKeyMapping())
            if self.find_updated_fields_funkey(funckey_model, funckey):
                updated_fields.append(position)
        return updated_fields

    def find_updated_fields_funkey(self, model, form):
        updated_fields = []
        for name, value in form.items():
            try:
                if isinstance(value, dict):
                    if self.find_updated_fields_funkey(getattr(model, name), value):
                        updated_fields.append(name)

                elif getattr(model, name) != value:
                    updated_fields.append(name)
            except AttributeError:
                pass
        return updated_fields


class FuncKeyDestination(ConfdResource):
    @required_acl('confd.funckeys.destinations.read')
    def get(self):
        return [
            {'type': type_, 'parameters': funckey().get_parameters()}
            for type_, funckey in FuncKeyDestinationField.destination_schemas.items()
        ]


class FuncKeyTemplateList(ListResource):

    context = {'exclude_destination': ['agent', 'bsfilter']}
    schema = FuncKeyTemplateSchema
    model = FuncKeyTemplate

    def build_headers(self, template):
        return {
            'Location': url_for('func_keys_templates', id=template.id, _external=True)
        }

    @required_acl('confd.funckeys.templates.read')
    def get(self):
        params = self.search_params()
        result = self.service.search(params)
        return {
            'total': result.total,
            'items': [
                self.schema(context=self.context).dump(item) for item in result.items
            ],
        }

    @required_acl('confd.funckeys.templates.create')
    def post(self):
        schema = self.schema(context=self.context)
        template = schema.load(request.get_json())
        template_model = self._create_template_model(template)
        model = self.service.create(template_model)
        return schema.dump(model), 201, self.build_headers(model)

    def _create_template_model(self, template):
        for position, funckey in template.get('keys', {}).items():
            template['keys'][position] = _create_funckey_model(funckey)
        return self.model(**template)


class FuncKeyTemplateItem(ConfdResource, FindUpdateFieldsMixin):

    context = {'exclude_destination': ['agent', 'bsfilter']}
    schema = FuncKeyTemplateSchema

    def __init__(self, service):
        super().__init__()
        self.service = service

    @required_acl('confd.funckeys.templates.{id}.read')
    def get(self, id):
        template = self.service.get(id)
        return self.schema(context=self.context).dump(template)

    @required_acl('confd.funckeys.templates.{id}.update')
    def put(self, id):
        template = self.service.get(id)
        template_form = self.schema().load(request.get_json())
        updated_fields = self.find_updated_fields_position(
            template.keys, template_form.get('keys', {})
        )

        for position, funckey in template_form.get('keys', {}).items():
            template_form['keys'][position] = _create_funckey_model(funckey)

        template.keys = template_form.get('keys', {})
        template.name = template_form.get('name')

        self.service.edit(template, updated_fields)
        return '', 204

    @required_acl('confd.funckeys.templates.{id}.delete')
    def delete(self, id):
        template = self.service.get(id)
        self.service.delete(template)
        return '', 204


class FuncKeyTemplateItemPosition(ItemResource):

    context = {'exclude_destination': ['agent', 'bsfilter']}
    schema = FuncKeySchema

    @required_acl('confd.funckeys.templates.{id}.{position}.read')
    def get(self, id, position):
        funckey = self.service.get(id).get(position)
        return self.schema(context=self.context).dump(funckey)

    @required_acl('confd.funckeys.templates.{id}.{position}.update')
    def put(self, id, position):
        template = self.service.get(id)
        funckey = self.schema(context=self.context).load(request.get_json())
        funckey_model = _create_funckey_model(funckey)
        self.service.edit_funckey(funckey_model, template, position)
        return '', 204

    @required_acl('confd.funckeys.templates.{id}.{position}.delete')
    def delete(self, id, position):
        template = self.service.get(id)
        self.service.delete_funckey(template, position)
        return '', 204


class UserFuncKey(ConfdResource):
    def __init__(self, service, user_dao, template_dao):
        super().__init__()
        self.service = service
        self.user_dao = user_dao
        self.template_dao = template_dao

    def get_user(self, user_id):
        return self.user_dao.get_by_id_uuid(user_id)


class UserFuncKeyList(UserFuncKey, FindUpdateFieldsMixin):

    schema = FuncKeyUnifiedTemplateSchema

    @required_acl('confd.users.{user_id}.funckeys.read')
    def get(self, user_id):
        template = self.service.get_unified_template(user_id)
        return self.schema().dump(template)

    @required_acl('confd.users.{user_id}.funckeys.update')
    def put(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        template = self.template_dao.get(user.private_template_id)
        template_form = self.schema().load(request.get_json())
        updated_fields = self.find_updated_fields_position(
            template.keys, template_form.get('keys', {})
        )

        for position, funckey in template_form.get('keys', {}).items():
            template_form['keys'][position] = _create_funckey_model(funckey)

        template.keys = template_form.get('keys', {})
        template.name = template_form.get('name')

        self.service.edit_user_template(user, template, updated_fields)
        return '', 204


class UserFuncKeyItemPosition(UserFuncKey):

    schema = FuncKeySchema

    @required_acl('confd.users.{user_id}.funckeys.{position}.update')
    def put(self, user_id, position):
        user = self.user_dao.get_by_id_uuid(user_id)
        template = self.template_dao.get(user.private_template_id)
        funckey = self.schema().load(request.get_json())
        funckey_model = _create_funckey_model(funckey)
        self.service.edit_user_funckey(user, funckey_model, template, position)
        return '', 204

    @required_acl('confd.users.{user_id}.funckeys.{position}.delete')
    def delete(self, user_id, position):
        user = self.user_dao.get_by_id_uuid(user_id)
        template = self.template_dao.get(user.private_template_id)
        self.service.delete_funckey(template, position)
        return '', 204

    @required_acl('confd.users.{user_id}.funckeys.{position}.read')
    def get(self, user_id, position):
        template = self.service.get_unified_template(user_id)
        funckey = template.get(position)
        return self.schema().dump(funckey)


class UserFuncKeyTemplate(ConfdResource):
    def __init__(self, service, user_dao, template_dao):
        super().__init__()
        self.service = service
        self.user_dao = user_dao
        self.template_dao = template_dao

    def get_user(self, user_id):
        return self.user_dao.get_by_id_uuid(user_id)


class UserFuncKeyTemplateAssociation(UserFuncKeyTemplate):
    @required_acl('confd.users.{user_id}.funckeys.templates.{template_id}.update')
    def put(self, user_id, template_id):
        user = self.get_user(user_id)
        template = self.template_dao.get(template_id)
        self.service.associate(user, template)
        return '', 204

    @required_acl('confd.users.{user_id}.funckeys.templates.{template_id}.delete')
    def delete(self, user_id, template_id):
        user = self.get_user(user_id)
        template = self.template_dao.get(template_id)
        self.service.dissociate(user, template)
        return '', 204


class UserFuncKeyTemplateGet(UserFuncKeyTemplate):

    schema = FuncKeyTemplateUserSchema

    @required_acl('confd.users.{user_id}.funckeys.templates.read')
    def get(self, user_id):
        user = self.get_user(user_id)
        result = self.service.find_all_by_user_id(user.id)
        return {
            'total': len(result),
            'items': [self.schema().dump(item) for item in result],
        }


class FuncKeyTemplateUserGet(UserFuncKeyTemplate):

    schema = FuncKeyTemplateUserSchema

    @required_acl('confd.funckeys.templates.{template_id}.users.read')
    def get(self, template_id):
        template = self.template_dao.get(template_id)
        result = self.service.find_all_by_template_id(template.id)
        return {
            'total': len(result),
            'items': [self.schema().dump(item) for item in result],
        }
