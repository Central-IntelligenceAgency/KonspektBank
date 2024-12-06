from .Attachment import Attachment


class Document(Attachment):
    def __init__(self, document, name):
        super().__init__(document, name)