
import re
import socket
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning


class Protocol:

    request_attempts = 3

    def __init__(self):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def request(self, request):
        result = {'status': 0}
        response = None

        if re.match('^https://', request['url']):
            request['verify'] = False

        attempts = self.request_attempts
        while attempts:
            try:
                response = self.session.request(**request)
                break

            except requests.exceptions.ConnectionError:
                result = {'status': -1, 'error': 'Connection Error'}

            except socket.timeout:
                result = {'status': -2, 'error': 'No response'}

            attempts -= 1

        return result, response
