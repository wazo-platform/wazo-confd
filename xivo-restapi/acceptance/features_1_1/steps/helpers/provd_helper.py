# -*- coding: UTF-8 -*-


from acceptance.features_1_1.steps.helpers.remote import remote_exec


def device_config_has_properties(device, properties):
    remote_exec(_device_config_has_properties, config=device.config, properties=dict(properties[0]))


def _device_config_has_properties(channel, config, properties):
    from xivo_dao.helpers import provd_connector

    provd_config_manager = provd_connector.config_manager()
    config = provd_config_manager.get(config)
    sip_lines = config['raw_config']['sip_lines']

    sip_line = sip_lines['1']

    keys = [u'username', u'auth_username', u'display_name', u'password', u'number']
    for key in keys:
        message = u"Invalid %s ('%s' instead of '%s')" % (key, sip_line[key], properties[key])
        message = message.encode('utf8')
        assert sip_line[key] == properties[key], message
