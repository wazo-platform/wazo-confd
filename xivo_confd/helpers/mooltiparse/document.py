class Document(object):

    def __init__(self, fields):
        self.fields = fields

    def validate(self, content, action=None):
        for field in self.fields:
            value = content.get(field.name)
            field.validate(value, action)

    def field_names(self):
        return tuple(f.name for f in self.fields)


class DocumentProxy(object):

    def __init__(self, parser, document):
        self.parser = parser
        self.document = document

    def parse(self, request, action=None):
        return self.parser.parse(request, self.document, action)

    def validate(self, content, action=None):
        return self.document.validate(content, action)

    def field_names(self):
        return self.document.field_names()
