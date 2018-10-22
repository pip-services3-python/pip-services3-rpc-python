# -*- coding: utf-8 -*-
"""
    pip_services_rpc.services.RestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    REST service implementation
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import bottle
import json
import time

from threading import Thread

from pip_services_commons.config import IConfigurable, ConfigParams
from pip_services_commons.refer import IReferenceable, DependencyResolver, IUnreferenceable
from pip_services_commons.run import IOpenable, IClosable
from pip_services_components.connect import ConnectionParams, ConnectionResolver
from pip_services_components.log import CompositeLogger
from pip_services_components.count import CompositeCounters
from pip_services_commons.errors import ConfigException, ConnectionException, InvalidStateException
from pip_services_commons.errors import ErrorDescription, ErrorDescriptionFactory
from pip_services_commons.data import FilterParams, PagingParams
from pip_services_commons.validate import Schema
from .IRegisterable import IRegisterable
from .HttpEndpoint import HttpEndpoint
from .HttpResponseSender import HttpResponseSender

from .SimpleServer import SimpleServer

class RestService(IOpenable, IConfigurable, IReferenceable, IUnreferenceable, IRegisterable):
    _default_config = ConfigParams.from_tuples("base_route", "",
                                               "dependencies.endpoint", "*:endpoint:http:*:1.0")
    _config = None
    _references = None
    _local_endpoint = None
    _opened = None

    _base_route = None
    _endpoint = None
    _dependency_resolver = DependencyResolver(_default_config)
    _logger = CompositeLogger()
    _counters = CompositeCounters()

    def configure(self, config):
        config = config.set_defaults(self._default_config)
        self._config = config

        self._dependency_resolver.configure(config)
        self._base_route = config.get_as_string_with_default("base_route", self._base_route)

    def set_references(self, references):
        self._references = references
        self._logger.set_references(references)
        self._counters.set_references(references)

        self._dependency_resolver.set_references(references)

        self._endpoint = self._dependency_resolver.get_one_optional('endpoint')

        if self._endpoint == None:
            self._endpoint = self.create_endpoint()
            self._local_endpoint = True
        else:
            self._local_endpoint = False

        self._endpoint.register(self)

    def unset_references(self):
        if self._endpoint != None:
            self._endpoint.unregister(self)
            self._endpoint = None

    def create_endpoint(self):
        endpoint = HttpEndpoint()
        if self._config != None:
            endpoint.configure(self._config)

        if self._references != None:
            endpoint.set_references(self._references)

        return endpoint

    def _instrument(self, correlation_id, name):
        self._logger.trace(correlation_id, "Executing " + name + " method")
        return self._counters.begin_timing(name + ".exec_time")

    def is_opened(self):
        return self._opened

    def open(self, correlation_id):
        if self.is_opened():
            return

        if self._endpoint == None:
            self._endpoint = self.create_endpoint()
            self._endpoint.register(self)
            self._local_endpoint = True

        if self._local_endpoint:
            self._endpoint.open(correlation_id)

        self._opened = True

    def close(self, correlation_id):
        if not self._opened:
            return

        if self._endpoint == None:
            raise InvalidStateException(correlation_id, "NO_ENDPOINT", "HTTP endpoint is missing")

        if self._local_endpoint:
            self._endpoint.close(correlation_id)

        self._opened = False

    def send_result(self, result):
        return HttpResponseSender.send_result(result)

    def send_created_result(self, result):
        return HttpResponseSender.send_created_result(result)

    def send_deleted_result(self):
        return HttpResponseSender.send_deleted_result()


    def send_error(self, error):
        return HttpResponseSender.send_error(error)


    def get_param(self, param, default = None):
        return bottle.request.params.get(param, default)


    def get_correlation_id(self):
        return bottle.request.query.get('correlation_id')


    def get_filter_params(self):
        data = dict(bottle.request.query.decode())
        data.pop('correlation_id', None)
        data.pop('skip', None)
        data.pop('take', None)
        data.pop('total', None)
        return FilterParams(data)


    def get_paging_params(self):
        skip = bottle.request.query.get('skip')
        take = bottle.request.query.get('take')
        total = bottle.request.query.get('total')
        return PagingParams(skip, take, total)


    def get_data(self):
         return bottle.request.json

    def register_route(self, method, route, schema, handler):
        if self._endpoint == None:
            return

        if self._base_route != None and len(self._base_route) > 0:
            base_route = self._base_route
            if base_route[0] != '/':
                base_route = '/' + base_route
            route = base_route + route

        self._endpoint.register_route(method, route, schema, handler)

    def register(self):
        pass