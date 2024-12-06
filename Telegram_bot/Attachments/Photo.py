from .Attachment import Attachment

class Photo(Attachment):
    def __init__(self, data, name):
        super().__init__(data, name)