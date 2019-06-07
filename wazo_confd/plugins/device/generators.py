# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class ConfigGenerator:

    def __init__(self, raw_generator):
        self.raw_generator = raw_generator

    def generate(self, device):
        configdevice = device.template_id or 'defaultconfigdevice'
        config = {
            'id': device.id,
            'configdevice': configdevice,
            'parent_ids': ['base', configdevice],
            'deletable': True,
            'raw_config': self.raw_generator.generate(device),
        }

        return config


class RawConfigGenerator:

    def __init__(self, generators):
        self.generators = generators

    def generate(self, device):
        raw_config = {'X_key': '',
                      'config_version': 1}

        for generator in self.generators:
            section = generator.generate(device)
            if section:
                raw_config.update(section)

        return raw_config


class UserGenerator:

    def __init__(self, device_db):
        self.device_db = device_db

    def generate(self, device):
        row = self.device_db.profile_for_device(device.id)
        if row:
            return {'X_xivo_user_uuid': row.uuid,
                    'X_xivo_phonebook_profile': row.context}


class ExtensionGenerator:

    def __init__(self, extension_dao):
        self.extension_dao = extension_dao

    def generate(self, device):
        return {
            'exten_dnd': self.find_exten('enablednd'),
            'exten_fwd_unconditional': self.find_exten('fwdunc'),
            'exten_fwd_no_answer': self.find_exten('fwdrna'),
            'exten_fwd_busy': self.find_exten('fwdbusy'),
            'exten_fwd_disable_all': self.find_exten('fwdundoall'),
            'exten_park': self.find_exten('parkext'),
            'exten_pickup_group': self.find_exten('pickupexten'),
            'exten_pickup_call': self.find_exten('pickup'),
            'exten_voicemail': self.find_exten('vmusermsg'),
        }

    def find_exten(self, typeval):
        extension = self.extension_dao.find_by(type='extenfeatures', typeval=typeval)
        if extension:
            return extension.clean_exten()


class FuncKeyGenerator:

    def __init__(self, user_dao, line_dao, user_line_dao, template_dao, device_dao, converters):
        self.user_dao = user_dao
        self.line_dao = line_dao
        self.user_line_dao = user_line_dao
        self.device_dao = device_dao
        self.template_dao = template_dao
        self.converters = converters

    def generate(self, device):
        user, line = self.user_line_for_device(device.id)
        if user and line:
            template = self.get_unified_template(user)
            funckeys = self.convert_funckeys(user, line, template)
            return {'funckeys': funckeys}

    def user_line_for_device(self, device_id):
        lines = self.line_dao.find_all_by(device=device_id)
        try:
            line = min(lines, key=lambda x: x.position)
        except ValueError:
            return None, None

        main_user_line = self.user_line_dao.find_main_user_line(line.id)
        if main_user_line:
            user = self.user_dao.get(main_user_line.user_id)
            return user, line
        return None, None

    def get_unified_template(self, user):
        private_template = self.template_dao.get(user.private_template_id)
        if user.func_key_template_id:
            public_template = self.template_dao.get(user.func_key_template_id)
            return public_template.merge(private_template)
        return private_template

    def convert_funckeys(self, user, line, template):
        funckeys = {}
        for pos, funckey in template.keys.items():
            converter = self.converters[funckey.destination.type]
            funckeys.update(converter.build(user, line, pos, funckey))
        return funckeys


class SipGenerator:

    def __init__(self, device_dao, device_db):
        self.device_dao = device_dao
        self.device_db = device_db

    def generate(self, device):
        sip_lines = {}
        rows = self.device_db.sip_lines_for_device(device.id)
        for row in rows:
            pos = row.LineFeatures.position
            sip_lines[pos] = self.generate_sip_line(row)

        if len(sip_lines) > 0:
            return {'protocol': 'SIP', 'sip_lines': sip_lines}

    def generate_sip_line(self, row):
        line = row.LineFeatures
        sip = row.UserSIP
        extension = row.Extension
        registrar = self.device_dao.get_registrar(line.configregistrar)

        config = {'auth_username': sip.name,
                  'username': sip.name,
                  'password': sip.secret,
                  'display_name': line.caller_id_name,
                  'number': extension.exten,
                  'registrar_ip': registrar['registrar_main'],
                  'proxy_ip': registrar['proxy_main']}

        proxy_backup = registrar.get('proxy_backup', '')
        if proxy_backup:
            config['backup_proxy_ip'] = proxy_backup
            config['backup_registrar_ip'] = registrar['registrar_backup']

        return config


class SccpGenerator:

    def __init__(self, device_dao, line_dao):
        self.device_dao = device_dao
        self.line_dao = line_dao

    def generate(self, device):
        call_managers = {}

        line = self.line_dao.find_by(device=device.id, protocol='sccp')
        if line:
            registrar = self.device_dao.get_registrar(line.configregistrar)
            proxy_backup = registrar.get('proxy_backup')

            call_managers['1'] = {'ip': registrar['proxy_main']}
            if proxy_backup:
                call_managers['2'] = {'ip': proxy_backup}

        if len(call_managers) > 0:
            return {'protocol': 'SCCP', 'sccp_call_managers': call_managers}
