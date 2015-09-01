

class Spider:

    status_codes  = [200]
    content_types = ['text/html']

    def __init__(self, unit):
        self.unit = unit

    def accept(self, response, content):
        if content['content-type'] in self.content_types:
            return True

        if response.status_code in self.status_codes:
            return True

        return False
