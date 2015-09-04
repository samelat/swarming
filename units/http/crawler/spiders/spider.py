

class Spider:

    status_codes  = [200]
    content_types = ['text/html']

    def __init__(self, unit):
        self.unit = unit

    def accept(self, content):
        try:
            if content['content-type'] not in self.content_types:
                return False

            if content['status-code'] not in self.status_codes:
                return False

        except KeyError:
            return False

        return True
