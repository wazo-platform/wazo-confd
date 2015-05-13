from xivo_confd.resources.devices.service import DeviceService, LineDeviceAssociationService, DeviceValidator, SearchEngine, LineDeviceUpdater
from xivo_confd.resources.devices.dao import ProvdDeviceDao, DeviceDao
from xivo_confd.resources.devices import notifier as device_notifier

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao


def build_service(device_dao, provd_dao):
    search_engine = SearchEngine(provd_dao)

    device_validator = DeviceValidator(device_dao, line_dao)

    device_service = DeviceService(device_dao,
                                   device_validator,
                                   device_notifier,
                                   search_engine,
                                   line_dao)

    return device_service


def build_provd_dao(provd_client):
    provd_dao = ProvdDeviceDao(provd_client.device_manager(),
                               provd_client.config_manager())
    return provd_dao


def build_dao(provd_client, provd_dao):
    device_dao = DeviceDao(provd_client, provd_dao)
    return device_dao


def build_line_device_updater(device_dao):
    line_device_updater = LineDeviceUpdater(line_dao,
                                            extension_dao,
                                            line_extension_dao,
                                            device_dao)
    return line_device_updater


def build_line_device_associator(updater):
    associator = LineDeviceAssociationService(line_dao,
                                              updater)
    return associator
