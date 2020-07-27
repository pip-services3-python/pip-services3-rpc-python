# -*- coding: utf-8 -*-
"""
    tests.rest.test_DummyCommandableHttpClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import pytest
import time

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import Descriptor, References, Referencer
from pip_services3_commons.run import Opener, Closer

from ..DummyController import DummyController
from .DummyClientFixture import DummyClientFixture
from .DummyCommandableHttpClient import DummyCommandableHttpClient
from ..services.DummyCommandableHttpService import DummyCommandableHttpService

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3001
)


class TestDummyCommandableHttpClient:
    references = None
    fixture = None

    @classmethod
    def setup_class(cls):
        cls.controller = DummyController()

        cls.service = DummyCommandableHttpService()
        cls.service.configure(rest_config)

        cls.client = DummyCommandableHttpClient()
        cls.client.configure(rest_config)

        cls.references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), cls.controller,
            Descriptor("pip-services-dummies", "service", "http", "default", "1.0"), cls.service
        )
        cls.client.set_references(cls.references)
        cls.service.set_references(cls.references)

        cls.fixture = DummyClientFixture(cls.client)

        cls.service.open(None)
        cls.client.open(None)
        time.sleep(1)

    @classmethod
    def teardown_class(cls):
        cls.service.close(None)
        cls.client.close(None)
        pass

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
