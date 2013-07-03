import os

from ConfigParser import ConfigParser

CONFIG_FILE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "config.ini.local"
    )
)


def get_config_value(section, key):
    if not os.path.exists(CONFIG_FILE_PATH):
        raise Exception("config file not found (%s)" % CONFIG_FILE_PATH)

    parser = ConfigParser()
    parser.read(CONFIG_FILE_PATH)
    return parser.get(section, key)
