

class Delimiter:

    def __init__(self, domain):
        self.zone = self.get_zone(domain)

    @staticmethod
    def get_zone(domain):
        return '.'.join(domain.split('.')[1:])

    def in_site(self, domain):
        pass

    def in_host(self, domain):
        pass

    def in_dns_zone(self, domain):
        pass

