

class Spider:

    status_codes  = []
    content_types = ['text/html']

    def __init__(self, unit):
        self.unit = unit

    def accept(self, content):
        if ('content-type' in content) and \
           (content['content-type'] in self.content_types):
            return True

        if ('status-code' in content) and \
           (content['status-code'] in self.status_codes):
            return True

        return False
