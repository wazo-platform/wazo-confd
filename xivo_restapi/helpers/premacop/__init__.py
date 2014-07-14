import json

from parser import Parser
from registry import ParserRegistry
from field import Field
from document import Document


def parser():
    registry = ParserRegistry()
    registry.register('application/json', parse_json)

    return Parser(registry)


def parse_json(content, document):
    return json.loads(content)
