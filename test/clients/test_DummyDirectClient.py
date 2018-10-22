# -*- coding: utf-8 -*-
"""
    tests.clients.test_DummyDirectClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services_commons.refer import Descriptor, References

from ..DummyController import DummyController
from .DummyClientFixture import DummyClientFixture
from .DummyDirectClient import DummyDirectClient

class TestDummyDirectClient:
    references = None
    fixture = None

    @classmethod
    def setup_class(cls):
        cls.controller = DummyController()
        
        cls.client = DummyDirectClient()

        cls.references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), cls.controller, 
            Descriptor("pip-services-dummies", "client", "direct", "default", "1.0"), cls.client
        )
        cls.client.set_references(cls.references)

        cls.fixture = DummyClientFixture(cls.client)

    def setup_method(self, method):
        self.client.open(None)

    def teardown_method(self, method):
        self.client.close(None)
        
    def test_crud_operations(self):
        self.fixture.test_crud_operations()

