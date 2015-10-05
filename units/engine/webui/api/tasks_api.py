
from .base_api import BaseAPI


class TasksAPI(BaseAPI):

    def __init__(self):
        super(TasksAPI, self).__init__('task')
