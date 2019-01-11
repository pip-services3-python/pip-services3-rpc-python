# -*- coding: utf-8 -*-
"""
    test_DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json
import time

import requests
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor
from pip_services3_commons.run import Parameters
from pip_services3_commons.data import IdGenerator

from ..Dummy import Dummy
from ..DummyController import DummyController
from ..services.DummyRestService import DummyRestService


rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3003
)


DUMMY1 = Dummy(None, 'Key 1', 'Content 1')
DUMMY2 = Dummy(None, 'Key 2', 'Content 2')

#todo return dummy object from response in invoke()
class TestDummyRestService():
    controller = None
    service = None

    @classmethod
    def setup_class(cls):
        cls.controller = DummyController()

        cls.service = DummyRestService()
        cls.service.configure(rest_config)

        cls.references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), cls.controller,
            Descriptor("pip-services-dummies", "service", "http", "default", "1.0"), cls.service
        )

        cls.service.set_references(cls.references)


    def setup_method(self, method):
        self.service.open(None)


    def teardown_method(self, method):
        self.service.close(None)

    # #todo
    def test_crud_operations(self):
        time.sleep(2)
        dummy1 = self.invoke("/dummies", json.loads(json.dumps(DUMMY1)))

        assert None != dummy1
        assert DUMMY1['key'] == dummy1['key']
        assert DUMMY1['content'] == dummy1['content']

    # todo return dummy object from response
    def invoke(self, route, entity):
        params = { }
        route = "http://localhost:3003" + route
        response = None
        timeout = 10000
        try:
            # Call the service
            response = requests.request('POST', route, params=params, json=json.dumps(entity), timeout=timeout)
            return response.json()
        except Exception as ex:
            # error = InvocationException(correlation_id, 'REST_ERROR', 'REST operation failed: ' + str(ex)).wrap(ex)
            # raise error
            return False