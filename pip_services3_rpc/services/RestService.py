# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.RestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    REST service implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import bottle
import json
import time

from threading import Thread

from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.refer import IReferenceable, DependencyResolver, IUnreferenceable
from pip_services3_commons.run import IOpenable, IClosable
from pip_services3_components.connect import ConnectionParams, ConnectionResolver
from pip_services3_components.log import CompositeLogger
from pip_services3_components.count import CompositeCounters
from pip_services3_commons.errors import ConfigException, ConnectionException, InvalidStateException
from pip_services3_commons.errors import ErrorDescription, ErrorDescriptionFactory
from pip_services3_commons.data import FilterParams, PagingParams
from pip_services3_commons.validate import Schema

from .IRegisterable import IRegisterable
from .HttpEndpoint import HttpEndpoint
from .HttpResponseSender import HttpResponseSender


class RestService(IOpenable, IConfigurable, IReferenceable, IUnreferenceable, IRegisterable):
    """
    Abstract service that receives remove calls via HTTP/REST protocol.

    ### Configuration parameters ###

    - base_route:              base route for remote URI
    - dependencies:
        - endpoint:              override for HTTP Endpoint dependency
        - controller:            override for Controller dependency
    - connection(s):
        - discovery_key:         (optional) a key to retrieve the connection from IDiscovery
        - protocol:              connection protocol: http or https
        - host:                  host name or IP address
        - port:                  port number
        - uri:                   resource URI or connection string with all parameters in it

    ### References ###

    - *:logger:*:*:1.0         (optional) ILogger components to pass log messages
    - *:counters:*:*:1.0         (optional) ICounters components to pass collected measurements
    - *:discovery:*:*:1.0        (optional) IDiscovery services to resolve connection
    - *:endpoint:http:*:1.0          (optional) HttpEndpoint reference

    Example:
        class MyRestService(RestService):
            _controller = None
            ...

            def __init__(self):
                super(MyRestService, self).__init__()
                self._dependencyResolver.put("controller", Descriptor("mygroup","controller","*","*","1.0"))

            def set_references(self, references):
                super(MyRestService, self).set_references(references)
                self._controller = self._dependencyResolver.get_required("controller")

            def register():
                ...

        service = MyRestService()
        service.configure(ConfigParams.from_tuples("connection.protocol", "http",
                                                       "connection.host", "localhost",
                                                       "connection.port", 8080))
        service.set_references(References.from_tuples(Descriptor("mygroup","controller","default","default","1.0"), controller))
        service.open("123")
    """
    _default_config = None
    _debug = False
    _dependency_resolver = None
    _logger = None
    _counters = None
    # _registered = None
    _local_endpoint = None
    _config = None
    _references = None
    _base_route = None
    _endpoint = None
    _opened = None

    def __init__(self):
        self._default_config = ConfigParams.from_tuples("base_route", None,
                                                        "dependencies.endpoint", "*:endpoint:http:*:1.0")
        # self._registered = False
        self._dependency_resolver = DependencyResolver()
        self._logger = CompositeLogger()
        self._counters = CompositeCounters()

    def _instrument(self, correlation_id, name):
        """
        Adds instrumentation to log calls and measure call time. It returns a Timing object that is used to end the time measurement.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param name: a method name.
        """
        self._logger.trace(correlation_id, "Executing " + name + " method")
        return self._counters.begin_timing(name + ".exec_time")

    def set_references(self, references):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._references = references
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._dependency_resolver.set_references(references)
        self._endpoint = self._dependency_resolver.get_one_optional('endpoint')

        if self._endpoint is None:
            self._endpoint = self.create_endpoint()
            self._local_endpoint = True
        else:
            self._local_endpoint = False

        self._endpoint.register(self)

    def configure(self, config):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        config = config.set_defaults(self._default_config)
        self._config = config
        self._dependency_resolver.configure(config)
        self._base_route = config.get_as_string_with_default("base_route", self._base_route)

    def unset_references(self):
        """
        Unsets (clears) previously set references to dependent components.
        """
        if not (self._endpoint is None):
            self._endpoint.unregister(self)
            self._endpoint = None

    def create_endpoint(self):
        endpoint = HttpEndpoint()
        if not (self._config is None):
            endpoint.configure(self._config)

        if not (self._references is None):
            endpoint.set_references(self._references)

        return endpoint

    def _instrument(self, correlation_id, name):
        self._logger.trace(correlation_id, f"Executing {name} method")
        self._counters.increment_one(f"{name}.exec_count")
        return self._counters.begin_timing(f"{name}.exec_time")

    def _instrument_error(self, correlation_id, name, error, result, callback):
        if not (error is None):
            self._logger.error(correlation_id, error, f"Failed to execute {name} method")
            self._counters.increment_one(f"{name}.exec_error")
        if not (callback is None):
            callback(error, result)

    def is_opened(self):
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self._opened

    def open(self, correlation_id):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """

        if self.is_opened():
            return

        if self._endpoint is None:
            self._endpoint = self.create_endpoint()
            self._endpoint.register(self)
            self._local_endpoint = True

        if self._local_endpoint:
            self._endpoint.open(correlation_id)

        self._opened = True
        # # register route
        # if self._registered != True:
        #     self.add_route()
        #     self._registered = True

    def close(self, correlation_id):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if not self._opened:
            return

        if self._endpoint is None:
            raise InvalidStateException(correlation_id, "NO_ENDPOINT", "HTTP endpoint is missing")

        if self._local_endpoint:
            self._endpoint.close(correlation_id)

        self._opened = False

    def send_result(self, result):
        """
        Creates a callback function that sends result as JSON object. That callack function call be called directly or passed as a parameter to business logic components.

        If object is not null it returns 200 status code. For null results it returns
        204 status code. If error occur it sends ErrorDescription with approproate status code.

        :param result: a body object to result.

        :return: execution result.
        """

        return HttpResponseSender.send_result(result)

    def send_created_result(self, result):
        """
        Creates a callback function that sends newly created object as JSON. That callack function call be called directly or passed as a parameter to business logic components.

        If object is not null it returns 201 status code. For null results it returns
        204 status code. If error occur it sends ErrorDescription with approproate status code.

        :param result: a body object to result.

        :return: execution result.
        """
        return HttpResponseSender.send_created_result(result)

    def send_deleted_result(self):
        """
        Creates a callback function that sends newly created object as JSON. That callack function call be called directly or passed as a parameter to business logic components.

        If object is not null it returns 200 status code. For null results it returns
        204 status code. If error occur it sends ErrorDescription with approproate status code.

        :return: execution result.
        """

        return HttpResponseSender.send_deleted_result()

    def send_error(self, error):
        """
        Sends error serialized as ErrorDescription object and appropriate HTTP status code. If status code is not defined, it uses 500 status code.

        :param error: an error object to be sent.
        """

        return HttpResponseSender.send_error(error)

    def fix_route(self, route) -> str:
        if (route is not None and len(route) > 0):
            if (route[0] != '/'):
                route = f'/{route}'
            return route

        return ''

    def register_route(self, method, route, schema, handler):
        """
        Registers an action in this objects REST server (service) by the given method and route.

        :param method: the HTTP method of the route.

        :param route: the route to register in this object's REST server (service).

        :param schema: the schema to use for parameter validation.

        :param handler: the action to perform at the given route.
        """
        if self._endpoint is None:
            return

        route = f"{self.fix_route(self._base_route)}{self.fix_route(route)}"
        # if not (self._base_route is None) and len(self._base_route) > 0:
        #     base_route = self._base_route
        #     if base_route[0] != '/':
        #         base_route = '/' + base_route
        #     if route[0] != '/':
        #         base_route = base_route + '/'
        #     route = base_route + route
        self._endpoint.register_route(method, route, schema, handler)

    def register(self):
        pass

    def get_data(self):
        data = bottle.request.json
        if isinstance(data, str):
            return json.loads(bottle.request.json)
        elif bottle.request.json:
            return bottle.request.json
        else:
            return None

    def get_request_param(self):

        if (not (bottle is None)) and (not (bottle.request is None)) and (not (bottle.request.params is None)):
            return bottle.request.params
        else:
            return {}

    # TODO: Add:
    # registerRouteWithAuth
    # registerInterceptor
