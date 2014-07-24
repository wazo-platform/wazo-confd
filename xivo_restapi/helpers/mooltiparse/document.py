class Document(object):

    def __init__(self, fields):
        self.fields = fields

    def validate(self, content, action=None):
        for field in self.fields:
            value = content.get(field.name)
            field.validate(value, action)


class DocumentProxy(object):

    def __init__(self, parser, document):
        self.parser = parser
        self.document = document

    def parse(self, request, action=None):
        return self.parser.parse(request, self.document, action)
