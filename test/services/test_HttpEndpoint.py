# -*- coding: utf-8 -*-
"""
    test.services.TestHttpEndpoint
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    HttpEndpoint test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json

import requests
from pip_services_commons.config import ConfigParams
from pip_services_commons.refer import References, Descriptor
from pip_services_commons.run import Parameters
from pip_services_rpc.services import HttpEndpoint

from ..Dummy import Dummy
from ..DummyController import DummyController
from .DummyRestService import DummyRestService

rest_config = ConfigParams.from_tuples("connection.protocol", "http",
                                         "connection.host", "localhost",
                                         "connection.port", 3000)
DUMMY1 = Dummy(None, 'Key 1', 'Content 1')
DUMMY2 = Dummy(None, 'Key 2', 'Content 2')

#todo return dummy object from response in invoke()
class TestHttpEndpoint():
    endpoint = None
    service = None

    @classmethod
    def setup_class(cls):
        cls.controller = DummyController()

        cls.service = DummyRestService()
        cls.service.configure(ConfigParams.from_tuples('base_route', '/api/v1'))

        cls.endpoint = HttpEndpoint()
        cls.endpoint.configure(rest_config)

        cls.references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), cls.controller,
            Descriptor("pip-services-dummies", "service", "rest", "default", "1.0"), cls.service,
            Descriptor("pip-services", "endpoint", "http", "default", "1.0"), cls.endpoint
        )
        cls.service.set_references(cls.references)

    def setup_method(self, method):
        self.endpoint.open(None)
        self.service.open(None)

    def teardown_method(self, method):
        self.endpoint.close(None)
        self.service.close(None)

    def test_crud_operations(self):
        dummy1 = self.invoke("/dummy/create_dummy", Parameters.from_tuples("dummy", DUMMY1))

        assert None != dummy1
        assert None != dummy1['id']
        assert DUMMY1['key'] == dummy1['key']
        assert DUMMY1['content'] == dummy1['content']

        #todo get_dummies

    #todo return dummy object from response
    def invoke(self, route, entity):
        response = requests.post("http://localhost:3000" + route, data=json.dumps(entity))
        return response