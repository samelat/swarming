
import requests
import dns.resolver
from urllib import parse

class Delimiter:

    def __init__(self, site):
        components = parse.urlparse(site)

        # Get DNS Zone
        self.zone = None
        labels = components.domain.split('.')
        while not self.zone:
            try:
                answer = dns.resolver.query('.'.join(labels), 'soa').response.answer
                soa_records = [record for record in answer if record.rdtype == 6]
                self.zone = soa_records[0].name

            except dns.resolver.NoAnswer:
                labels.pop(0)

        # Make a sign using the HTTP response headers
        requests.get(site)
        self.sign = {}

    def url_site(self, url):
        components = parse.urlparse(url)

    def in_dns_zone(self, domain):
        return dns.name.from_text(domain).is_subdomain(self.zone)

    def in_site(self, url):
        return True

if __name__ == "__main__":

    import sys
    delimiter = Delimiter(sys.argv[1])
    print('[!] {0}'.format(delimiter.zone))