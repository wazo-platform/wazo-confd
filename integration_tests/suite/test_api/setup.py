import os
import subprocess
import logging

from client import ConfdClient

logger = logging.getLogger(__name__)

ASSETS_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
ASSET_PATH = os.path.join(ASSETS_ROOT, 'base')


def new_client(headers=None):
    xivo_host = os.environ.get('HOST', 'localhost')
    xivo_confd_port = os.environ.get('PORT', 9486)
    xivo_confd_login = os.environ.get('LOGIN', 'admin')
    xivo_confd_password = os.environ.get('PASSWORD', 'proformatique')
    xivo_https = bool(os.environ.get('HTTPS', ''))
    client = ConfdClient.from_options(host=xivo_host,
                                      port=xivo_confd_port,
                                      username=xivo_confd_login,
                                      password=xivo_confd_password,
                                      https=xivo_https,
                                      headers=headers)
    return client


def new_confd(headers=None):
    return new_client(headers).url


def setup_docker():
    cleanup_docker()
    start_docker()


def stop_docker():
    os.chdir(ASSET_PATH)
    run_cmd(('docker-compose', 'kill'))


def cleanup_docker():
    os.chdir(ASSET_PATH)
    run_cmd(('docker-compose', 'kill'))
    run_cmd(('docker-compose', 'rm', '-f'))


def start_docker():
    os.chdir(ASSET_PATH)
    run_cmd(('docker-compose', 'run', '--rm', '--service-ports', 'testdeps'))
    run_cmd(('docker-compose', 'run', '--rm', '--service-ports', 'tests'))


def run_cmd(cmd):
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    out, _ = process.communicate()
    logger.info(out)
    return out
