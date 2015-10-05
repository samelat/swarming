
from .base_api import BaseAPI


class DictionariesAPI(BaseAPI):

    def __init__(self):
        super(DictionariesAPI, self).__init__('dictionary')
