import json

from parser import Parser
from registry import ParserRegistry
from field import Field
from document import Document
from types import *
from validators import *


def parser():
    registry = ParserRegistry()
    registry.register('application/json', parse_json)

    return Parser(registry)


def parse_json(content, document):
    return json.loads(content.decode('utf8'))
