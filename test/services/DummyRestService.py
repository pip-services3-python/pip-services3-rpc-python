# -*- coding: utf-8 -*-
"""
    test.rest.DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy REST service
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json

import bottle
from pip_services3_commons.convert import TypeCode
from pip_services3_commons.data import FilterParams, PagingParams
from pip_services3_commons.refer import Descriptor
from pip_services3_commons.validate import ObjectSchema, FilterParamsSchema

from pip_services3_rpc.services import AboutOperations
from pip_services3_rpc.services import RestService
from ..DummySchema import DummySchema


class DummyRestService(RestService):

    def __init__(self):
        super(DummyRestService, self).__init__()
        # self._controller = DummyRestOperations()
        self._dependency_resolver.put('controller',
                                      Descriptor("pip-services-dummies", "controller", "default", "*", "*"))

        self._controller = None
        self._number_of_calls = 0
        self._open_api_content = None
        self._open_api_file = None

    def configure(self, config):
        super().configure(config)

        self._open_api_content = config.get_as_nullable_string("openapi_content")
        self._open_api_file = config.get_as_nullable_string('openapi_file')

    def set_references(self, references):
        super().set_references(references)
        self._controller = self._dependency_resolver.get_one_required('controller')

    def get_number_of_calls(self) -> int:
        return self._number_of_calls

    def _increment_number_of_calls(self, req=None, res=None):
        self._number_of_calls += 1

    def __get_page_by_filter(self):
        return self._controller.get_page_by_filter(
            bottle.request.query.get('correlation_id'),
            FilterParams(bottle.request.query.dict),
            PagingParams(bottle.request.query.get('skip'),
                         bottle.request.query.get('take'),
                         bottle.request.query.get('total')),
        ).to_json()

    def __get_one_by_id(self, id):
        return self._controller.get_one_by_id(
            bottle.request.query.get('correlation_id'),
            bottle.request.query.get('id'),
        )

    def __create(self):
        return self._controller.create(
            bottle.request.query.get('correlation_id'),
            json.loads(bottle.request.json).get('body'),
        )

    def __update(self):
        return self._controller.update(
            bottle.request.query.get('correlation_id'),
            json.loads(bottle.request.json).get('body'),
        )

    def __delete_by_id(self, id):
        return self._controller.delete_by_id(
            bottle.request.query.get('correlation_id'),
            bottle.request.query.get('dummy_id'),
        )

    def register(self):
        self.register_interceptor('/dummies', self._increment_number_of_calls)

        self.register_route('get', '/dummies', ObjectSchema(True)
                            .with_optional_property("skip", TypeCode.String)
                            .with_optional_property("take", TypeCode.String)
                            .with_optional_property("total", TypeCode.String)
                            .with_optional_property("body", FilterParamsSchema()), self.__get_page_by_filter)

        self.register_route('get', '/dummies/<id>', ObjectSchema(True)
                            .with_required_property("id", TypeCode.String),
                            self.__get_one_by_id)

        self.register_route('post', '/dummies', ObjectSchema(True)
                            .with_required_property("body", DummySchema()),
                            self.__create)

        self.register_route('put', '/dummies', ObjectSchema(True)
                            .with_required_property("body", DummySchema()),
                            self.__update)

        self.register_route('delete', '/dummies/<id>', ObjectSchema(True)
                            .with_required_property("dummy_id", TypeCode.String),
                            self.__delete_by_id)

        self.register_route('post', '/about', None, AboutOperations().get_about)

        if self._open_api_content:
            self._register_open_api_spec(self._open_api_content)

        if self._open_api_file:
            self._register_open_api_spec_from_file(self._open_api_file)
