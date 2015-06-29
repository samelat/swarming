
import requests

from modules.dictionary import Dictionary


class Get:

    def __init__(self, unit):
        self.unit = unit

    def crack(self, dictionaries):

        print('[<#########>] {0}'.format(self.unit.task))

        for username, password in Dictionary(dictionaries).join():
            print('[http] Forcing Username: {0} - Password: {1}'.format(username, password))
        time.sleep(5)

        return {'status':0}