

class Spider:

    content_types = []

    def __init__(self, unit):
        self.unit = unit

    def accept(self, response, extra):
        if extra['content-type'] in self.content_types:
            return True
