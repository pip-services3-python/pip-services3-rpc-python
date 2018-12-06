# -*- coding: utf-8 -*-
"""
    pip_services_rpc.rest.RestService
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
from pip_services_commons.errors import ConfigException, ConnectionException
from pip_services_commons.errors import ErrorDescription, ErrorDescriptionFactory
from pip_services_commons.data import FilterParams, PagingParams
from pip_services_commons.validate import Schema

from .SimpleServer import SimpleServer
from .IRegisterable import IRegisterable
from .HttpEndpoint import HttpEndpoint
from .HttpResponseSender import HttpResponseSender

class RestService(IOpenable, IConfigurable, IReferenceable, IUnreferenceable, IRegisterable):
    _default_config = None
    _debug = False
    _dependency_resolver = None
    _logger = None
    _counters = None
    _registered = None
    _local_endpoint = None
    _config = None
    _references = None
    _base_route = None
    _opened = None

    def __init__(self):
        self._default_config = ConfigParams.from_tuples("base_route", "",
                                                "dependencies.endpoint", "*:endpoint:http:*:1.0")
        self._registered = False
        self._dependency_resolver = DependencyResolver()
        self._logger = CompositeLogger()
        self._counters = CompositeCounters()

    def _instrument(self, correlation_id, name):
        self._logger.trace(correlation_id, "Executing " + name + " method")
        return self._counters.begin_timing(name + ".exec_time")


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

    def configure(self, config):
        config = config.set_defaults(self._default_config)
        self._config = config
        self._dependency_resolver.configure(config)
        self._base_route = config.get_as_string_with_default("base_route", self._base_route)

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
        # regester route
        if self._registered != True:
            self.add_route()
            self._registered = True

    def close(self, correlation_id):
        if not self._opened:
            return

        if self._endpoint == None:
            raise InvalidStateException(correlation_id, "NO_ENDPOINT", "HTTP endpoint is missing")

        if self._local_endpoint:
            self._endpoint.close(correlation_id)

        self._opened = False

    def _to_json(self, obj):
        if obj == None:
            return None

        if isinstance(obj, set):
            obj = list(obj)
        if isinstance(obj, list):
            result = []
            for item in obj:
                item = self._to_json(item)
                result.append(item)
            return result

        if isinstance(obj, dict):
            result = {}
            for (k, v) in obj.items():
                v = self._to_json(v)
                result[k] = v
            return result
        
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        if hasattr(obj, '__dict__'):
            return self._to_json(obj.__dict__)
        return obj


    def send_result(self, result):
        bottle.response.headers['Content-Type'] = 'application/json'
        if result == None: 
            bottle.response.status = 404
            return
        else:
            bottle.response.status = 200
            return json.dumps(result, default=self._to_json)


    def send_created_result(self, result):
        bottle.response.headers['Content-Type'] = 'application/json'
        if result == None: 
            bottle.response.status = 404
            return
        else:
            bottle.response.status = 201
            return json.dumps(result, default=self._to_json)


    def send_deleted_result(self):
        bottle.response.headers['Content-Type'] = 'application/json'
        bottle.response.status = 204
        return


    def send_error(self, error):
        bottle.response.headers['Content-Type'] = 'application/json'
        error = ErrorDescriptionFactory.create(error)
        if error.correlation_id == None:
            error.correlation_id = self.get_correlation_id()
        bottle.response.status = error.status
        return json.dumps(error.to_json())

    # def send_result(self, result):
    #     return HttpResponseSender.send_result(result)

    # def send_created_result(self, result):
    #     return HttpResponseSender.send_created_result(result)

    # def send_deleted_result(self):
    #     return HttpResponseSender.send_deleted_result()


    # def send_error(self, error):
    #     return HttpResponseSender.send_error(error)


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

    def add_route(self):
        pass