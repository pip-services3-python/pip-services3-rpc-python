# -*- coding: utf-8 -*-
"""
    test.rest.DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy REST service
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import threading

from pip_services3_commons.data import FilterParams, PagingParams, IdGenerator
from pip_services3_commons.refer import Descriptor
from pip_services3_rpc.services import RestService
from .DummyRestOperations import DummyRestOperations 
from pip_services3_rpc.services import AboutOperations

class DummyRestService(RestService):

    _operations = None
    _number_of_calls = 0

    def __init__(self):
        super(DummyRestService, self).__init__()
        self._operations = DummyRestOperations()

    def set_references(self, references):
        super(DummyRestService, self).set_references(references)
        self._operations.set_references(references)

    def get_number_of_calls() -> int:
        return self._number_of_calls

    def _increment_number_of_calls(): 
        self._number_of_calls += 1

    def register(self):
        # TODO: realize interseptor
        # self.register_interceptor('/dummies', self._increment_number_of_calls)
        self.register_route('get', '/dummies', None, self._operations.get_page_by_filter)
        self.register_route('get', '/dummies/<id>', None, self._operations.get_one_by_id)
        self.register_route('post', '/dummies', None, self._operations.create)
        self.register_route('put', '/dummies/<id>', None, self._operations.update)
        self.register_route('delete', '/dummies/<id>', None, self._operations.delete_by_id)
        self.register_route('get', '/dummies/handled_error', None, self._operations.handled_error)
        self.register_route('get', '/dummies/unhandled_error', None, self._operations.unhandled_error)
        self.register_route('post', '/about', None, AboutOperations().get_about)
