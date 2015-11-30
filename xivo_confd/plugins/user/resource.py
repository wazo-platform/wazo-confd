from flask import url_for, request
from flask_restful import reqparse, inputs, fields, marshal

from xivo_confd.helpers.restful import FieldList, Link, ListResource, ItemResource, Strict
from xivo_dao.alchemy.userfeatures import UserFeatures as User


MOBILE_PHONE_NUMBER_REGEX = r"^\+?[0-9\*#]+$"
CALLER_ID_REGEX = r'^"(.*)"( <\+?\d+>)?$'


user_fields = {
    'id': fields.Integer,
    'uuid': fields.String,
    'firstname': fields.String,
    'lastname': fields.String,
    'timezone': fields.String,
    'language': fields.String,
    'description': fields.String,
    'caller_id': fields.String,
    'outgoing_caller_id': fields.String,
    'mobile_phone_number': fields.String,
    'username': fields.String,
    'password': fields.String,
    'music_on_hold': fields.String,
    'preprocess_subroutine': fields.String,
    'userfield': fields.String,
    'links': FieldList(Link('users'))
}

directory_fields = {
    'id': fields.Integer,
    'line_id': fields.Integer,
    'agent_id': fields.Integer,
    'firstname': fields.String,
    'lastname': fields.String,
    'exten': fields.String,
    'mobile_phone_number': fields.String,
    'voicemail_number': fields.String,
    'userfield': fields.String,
    'description': fields.String
}

parser = reqparse.RequestParser()
parser.add_argument('firstname', type=Strict(unicode), store_missing=False)
parser.add_argument('lastname', type=Strict(unicode), store_missing=False)
parser.add_argument('timezone', type=Strict(unicode), store_missing=False)
parser.add_argument('language', type=Strict(unicode), store_missing=False)
parser.add_argument('description', type=Strict(unicode), store_missing=False)
parser.add_argument('outgoing_caller_id', type=Strict(unicode), store_missing=False)
parser.add_argument('username', type=Strict(unicode), store_missing=False)
parser.add_argument('password', type=Strict(unicode), store_missing=False)
parser.add_argument('music_on_hold', type=Strict(unicode), store_missing=False)
parser.add_argument('preprocess_subroutine', type=Strict(unicode), store_missing=False)
parser.add_argument('userfield', type=Strict(unicode), store_missing=False)
parser.add_argument('caller_id',
                    store_missing=False, type=inputs.regex(CALLER_ID_REGEX))
parser.add_argument('mobile_phone_number',
                    store_missing=False, type=inputs.regex(MOBILE_PHONE_NUMBER_REGEX))


class UserList(ListResource):

    model = User
    fields = user_fields

    parser = reqparse.RequestParser()
    parser.add_argument('firstname', type=Strict(unicode), required=True)
    parser.add_argument('lastname', type=Strict(unicode))
    parser.add_argument('timezone', type=Strict(unicode))
    parser.add_argument('language', type=Strict(unicode))
    parser.add_argument('description', type=Strict(unicode))
    parser.add_argument('outgoing_caller_id', type=Strict(unicode))
    parser.add_argument('username', type=Strict(unicode))
    parser.add_argument('password', type=Strict(unicode))
    parser.add_argument('music_on_hold', type=Strict(unicode))
    parser.add_argument('preprocess_subroutine', type=Strict(unicode))
    parser.add_argument('userfield', type=Strict(unicode))
    parser.add_argument('caller_id', type=inputs.regex(CALLER_ID_REGEX))
    parser.add_argument('mobile_phone_number', type=inputs.regex(MOBILE_PHONE_NUMBER_REGEX))

    def build_headers(self, user):
        return {'Location': url_for('users', id=user.id, _external=True)}

    def get(self):
        if request.args.get('view') == 'directory':
            fields = directory_fields
        else:
            fields = user_fields

        params = {key: request.args[key] for key in request.args}
        total, items = self.service.search(params)

        return {'total': total,
                'items': [marshal(item, fields) for item in items]}


class UserItem(ItemResource):

    fields = user_fields
    parser = parser


class UserUuidItem(ItemResource):

    fields = user_fields
    parser = parser

    def get(self, uuid):
        user = self.service.get_by(uuid=str(uuid))
        return marshal(user, self.fields)

    def put(self, uuid):
        user = self.service.get_by(uuid=str(uuid))
        self.parse_and_update(user)
        return '', 204

    def delete(self, uuid):
        user = self.service.get_by(uuid=str(uuid))
        self.service.delete(user)
        return '', 204
