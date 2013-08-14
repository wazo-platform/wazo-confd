# -*- coding: UTF-8 -*-


from acceptance.features_1_1.steps.helpers.remote import remote_exec


def device_config_has_properties(device, properties):
    remote_exec(_device_config_has_properties, config=device.config, properties=dict(properties[0]))


def _device_config_has_properties(channel, config, properties):
    from xivo_dao.helpers import provd_connector

    provd_config_manager = provd_connector.config_manager()
    config = provd_config_manager.get(config)
    sip_lines = config['raw_config']['sip_lines']
    assert sip_lines['1']['username'] == properties['username'], 'Invalid Username'
    assert sip_lines['1']['auth_username'] == properties['auth_username'], 'Invalid Auth Username'
    assert sip_lines['1']['display_name'] == properties['display_name'], 'Invalid Display Name'
    assert sip_lines['1']['password'] == properties['password'], 'Invalid Password'
    assert sip_lines['1']['number'] == properties['number'], 'Invalid Number'
