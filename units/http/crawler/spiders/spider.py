

class Spider:

    content_types = ['text/html']
    status_codes  = [200]

    def __init__(self, unit):
        self.unit = unit

    def accept(self, response, extra):
        if extra['content-type'] not in self.content_types:
            return False

        if response.status_code not in self.status_codes:
            return False

        return True
