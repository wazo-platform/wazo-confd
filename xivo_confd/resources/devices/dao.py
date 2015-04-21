import logging

from xivo_dao.data_handler import errors

from xivo_confd.resources.devices.model import ProvdDevice, DeviceConverter, ConfigConverter, EmptyConfigConverter

logger = logging.getLogger(__name__)


class DeviceDao(object):

    def __init__(self, client, provd_dao):
        self.provd_dao = provd_dao
        self.client = client

    def get(self, device_id):
        provd_device = self._get_provd_device(device_id)
        return provd_device.extract_model()

    def _get_provd_device(self, device_id):
        provd_device = self.provd_dao.find_by('id', device_id)
        if not provd_device:
            raise errors.not_found('Device', id=device_id)
        return provd_device

    def find_by(self, name, value):
        provd_device = self.provd_dao.find_by(name, value)
        return provd_device.extract_model() if provd_device else None

    def create(self, model):
        provd_device = self.provd_dao.create()
        provd_device.update(model)
        self.provd_dao.edit(provd_device)
        return provd_device.extract_model()

    def edit(self, model):
        provd_device = self._get_provd_device(model.id)
        provd_device.update(model)
        self.provd_dao.edit(provd_device)

    def delete(self, model):
        provd_device = self._get_provd_device(model.id)
        self.provd_dao.delete(provd_device)

    def reset_autoprov(self, model):
        provd_device = self._get_provd_device(model.id)
        self.provd_dao.reset_autoprov(provd_device)

    def synchronize(self, model):
        self.client.device_manager().synchronize(model.id)

    def update_lines(self, model, lines):
        provd_device = self.get(model.id)
        provd_device.update_lines(lines)
        self.provd_dao.edit(provd_device)

    def plugins(self):
        return self.client.plugin_manager().plugins()

    def device_templates(self):
        templates = self.client.config_manager().find({'X_type': 'device'})
        logger.info("found templates %s", templates)
        return [t['id'] for t in templates]


class ProvdDeviceDao(object):

    DIRECTION = {'asc': 1,
                 'desc': -1}

    def __init__(self, device_manager, config_manager):
        self.device_manager = device_manager
        self.config_manager = config_manager

    def find_by(self, name, value):
        devices = self.device_manager.find({name: value})
        logger.info("find by %s %s found %s", name, value, devices)
        if devices:
            return self.build_provd_device(devices[0])
        return None

    def build_provd_device(self, device):
        device_converter = DeviceConverter(device)
        config_converter = self._build_config_converter(device)
        return ProvdDevice(device_converter, config_converter)

    def _build_config_converter(self, device):
        config_id = device.get('config', device['id'])
        config = self._find_config(config_id)
        return ConfigConverter(config) if config else EmptyConfigConverter()

    def _find_config(self, config_id):
        configs = self.config_manager.find({'id': config_id})
        return configs[0] if configs else None

    def find_all_devices(self, order, direction):
        sort_direction = self.DIRECTION[direction]
        return self.device_manager.find(sort=(order, sort_direction))

    def create(self):
        device_id = self.device_manager.add({})
        logger.info("new device %s created", device_id)

        config = {'id': device_id,
                  'parent_ids': ['base'],
                  'deletable': True,
                  'raw_config': {}}

        logger.info("adding config %s", config)
        self.config_manager.add(config)
        return self.find_by('id', device_id)

    def edit(self, provd_device):
        device = provd_device.extract_device()
        config = provd_device.extract_config()

        logger.info("updating device %s", device)
        self.device_manager.update(device)
        logger.info("updating config %s", config)
        self.config_manager.update(config)

    def delete(self, provd_device):
        self.device_manager.remove(provd_device.device_id)
        self.config_manager.remove(provd_device.config_id)

    def reset_autoprov(self, provd_device):
        self.config_manager.remove(provd_device.config_id)
        autoprov_id = self.config_manager.autocreate()
        autoprov_config = self.config_manager.get(autoprov_id)
        provd_device.reset_autoprov(autoprov_config)
        self.edit(provd_device)
