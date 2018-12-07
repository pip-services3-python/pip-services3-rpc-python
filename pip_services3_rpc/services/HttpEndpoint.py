# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.HttpEndpoint
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Http endpoint implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from threading import Thread

import bottle

from pip_services3_commons.config import IConfigurable, ConfigParams
from pip_services3_commons.errors import ConnectionException, ConfigException
from pip_services3_commons.refer import IReferenceable, DependencyResolver
from pip_services3_commons.run import IOpenable
from pip_services3_commons.validate import Schema
from pip_services3_components.count import CompositeCounters
from pip_services3_components.log import CompositeLogger
from .IRegisterable import IRegisterable
from .SimpleServer import SimpleServer
from .HttpResponseSender import HttpResponseSender

from ..connect.HttpConnectionResolver import HttpConnectionResolver


class HttpEndpoint(IOpenable, IConfigurable, IReferenceable):
    """
    Used for creating HTTP endpoints. An endpoint is a URL, at which a given service can be accessed by a client.

    ### Configuration parameters ###

    Parameters to pass to the [[configure]] method for component configuration:

    - connection(s) - the connection resolver's connections;
        - "connection.discovery_key" - the key to use for connection resolving in a discovery service;
        - "connection.protocol" - the connection's protocol;
        - "connection.host" - the target host;
        - "connection.port" - the target port;
        - "connection.uri" - the target URI.

    ### References ###

    A logger, counters, and a connection resolver can be referenced by passing the following references to the object's [[setReferences]] method:

    - *:logger:*:*:1.0         (optional) ILogger components to pass log messages
    - *:counters:*:*:1.0         (optional) ICounters components to pass collected measurements
    - *:discovery:*:*:1.0        (optional) IDiscovery services to resolve connection

    Example:
        def my_method(_config, _references):
            endpoint = HttpEndpoint()
            if (_config)
                endpoint.configure(_config)
            if (_references)
                endpoint.setReferences(_references)
            ...

            endpoint.open(correlationId)
            ...
    """
    _default_config = None
    _connection_resolver = None
    _logger = None
    _counters = None
    _registrations = None
    _service = None
    _server = None
    _debug = False
    #_resource = None
    _uri = None
    #_dependency_resolver = DependencyResolver()

    def __init__(self):
        """
        Creates HttpEndpoint
        """
        self._default_config = ConfigParams.from_tuples("connection.protocol", "http",
                                                "connection.host", "0.0.0.0",
                                                "connection.port", 3000,
                                                "connection.request_max_size", 1024 * 1024,
                                                "connection.connect_timeout", 60000,
                                                "connection.debug", True)
        self._connection_resolver = HttpConnectionResolver()
        self._logger = CompositeLogger()
        self._counters = CompositeCounters()
        self._registrations = []

    def configure(self, config):
        """
        Configures this HttpEndpoint using the given configuration parameters.

        - connection(s) - the connection resolver's connections;
            - "connection.discovery_key" - the key to use for connection resolving in a discovery service;
            - "connection.protocol" - the connection's protocol;
            - "connection.host" - the target host;
            - "connection.port" - the target port;
            - "connection.uri" - the target URI.

        Args:
            config: configuration parameters, containing a "connection(s)" section.
        """
        config = config.set_defaults(self._default_config)
        self._connection_resolver.configure(config)

    def set_references(self, references):
        """
        Sets references to this endpoint's logger, counters, and connection resolver.

        - *:logger:*:*:1.0         (optional) ILogger components to pass log messages
        - *:counters:*:*:1.0         (optional) ICounters components to pass collected measurements
        - *:discovery:*:*:1.0        (optional) IDiscovery services to resolve connection

        Args:
            references: an IReferences object, containing references to a logger, counters, and a connection resolver.
        """
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._connection_resolver.set_references(references)

    def is_opened(self):
        """
        Checks if the component is opened.

        Returns:
            whether or not this endpoint is open with an actively listening REST server.
        """
        return self._server != None

    def open(self, correlation_id):
        """
        Opens a connection using the parameters resolved by the referenced connection resolver and creates a REST server (service) using the set options and parameters.

        Args:
            correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.is_opened():
            return

        connection = self._connection_resolver.resolve(correlation_id)
        if connection == None:
            raise ConfigException(correlation_id, "NO_CONNECTION", "Connection for REST client is not defined")
        self._uri = connection.get_uri()

        # Create instance of bottle application
        self._service = bottle.Bottle(catchall = True, autojson = True)

        # Enable CORS requests
        self._service.add_hook('after_request', self._enable_cors)
        self._service.route('/', 'OPTIONS', self._options_handler)
        self._service.route('/<path:path>', 'OPTIONS', self._options_handler)
        def start_server():
            self._service.run(server = self._server, debug = self._debug)

        host = connection.get_host()
        port = connection.get_port()
        # Starting service
        try:
            self._server = SimpleServer(host = host, port = port)

            # Start server in thread
            Thread(target=start_server).start()

            # Give 2 sec for initialization
            #time.sleep(2)
            self._connection_resolver.register(correlation_id)
            self._logger.debug(correlation_id, "Opened REST service at %s", self._uri)
        except Exception as ex:
            self._server = None

            raise ConnectionException(correlation_id, 'CANNOT_CONNECT', 'Opening REST service failed') \
                .wrap(ex).with_details('url', self._uri)

    def close(self, correlation_id):
        """
        Closes this endpoint and the REST server (service) that was opened earlier.

        Args:
            correlation_id: (optional) transaction id to trace execution through call chain.
        """
        try:
            if self._server != None:
                self._server.shutdown()
                self._logger.debug(correlation_id, "Closed REST service at %s", self._uri)

            self._server = None
            self._uri = None
        except Exception as ex:
            self._logger.warn(correlation_id, "Failed while closing REST service: " + str(ex))

    def register(self, registration):
        """
        Registers a registerable object for dynamic endpoint discovery.

        Args:
            registration: the registration to add.
        """
        self._registrations.append(registration)

    def unregister(self, registration):
        """
        Unregisters a registerable object, so that it is no longer used in dynamic endpoint discovery.

        Args:
            registration: the registration to remove.
        """
        self._registrations.remove(registration)

    def perform_registrations(self):
        for registration in self._registrations:
            registration.register()

    def register_route(self, method, route, schema, handler):
        """
        Registers an action in this objects REST server (service) by the given method and route.

        Args:
            method: the HTTP method of the route.

            route: the route to register in this object's REST server (service).

            schema: the schema to use for parameter validation.

            handler: the action to perform at the given route.
        """
        method = method.upper()

        def wrapper(*args, **kwargs):
            try:
                if isinstance(schema, Schema):
                    params = self.get_data()
                    correlation_id = params['correlation_id'] if 'correlation_id' in params else None
                    error = schema.validate_and_throw_exception(correlation_id, params, False)

                return handler(*args, **kwargs)
            except Exception as ex:
                return HttpResponseSender.send_error(ex)
                # return self.send_error(ex)

        self._service.route(route, method, wrapper)

    def get_data(self):
         return bottle.request.json

    def _enable_cors(self):
        bottle.response.headers['Access-Control-Allow-Origin'] = '*'
        bottle.response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
        bottle.response.headers['Access-Control-Allow-Headers'] = 'Authorization, Origin, Accept, Content-Type, X-Requested-With'

    def _options_handler(self, ath = None):
        return


    # def _to_json(self, obj):
    #     if obj == None:
    #         return None

    #     if isinstance(obj, set):
    #         obj = list(obj)
    #     if isinstance(obj, list):
    #         result = []
    #         for item in obj:
    #             item = self._to_json(item)
    #             result.append(item)
    #         return result

    #     if isinstance(obj, dict):
    #         result = {}
    #         for (k, v) in obj.items():
    #             v = self._to_json(v)
    #             result[k] = v
    #         return result
        
    #     if hasattr(obj, 'to_json'):
    #         return obj.to_json()
    #     if hasattr(obj, '__dict__'):
    #         return self._to_json(obj.__dict__)
    #     return obj


    # def send_result(self, result):
    #     bottle.response.headers['Content-Type'] = 'application/json'
    #     if result == None: 
    #         bottle.response.status = 404
    #         return
    #     else:
    #         bottle.response.status = 200
    #         return json.dumps(result, default=self._to_json)


    # def send_created_result(self, result):
    #     bottle.response.headers['Content-Type'] = 'application/json'
    #     if result == None: 
    #         bottle.response.status = 404
    #         return
    #     else:
    #         bottle.response.status = 201
    #         return json.dumps(result, default=self._to_json)


    # def send_deleted_result(self):
    #     bottle.response.headers['Content-Type'] = 'application/json'
    #     bottle.response.status = 204
    #     return


    # def send_error(self, error):
    #     bottle.response.headers['Content-Type'] = 'application/json'
    #     error = ErrorDescriptionFactory.create(error)
    #     if error.correlation_id == None:
    #         error.correlation_id = self.get_correlation_id()
    #     bottle.response.status = error.status
    #     return json.dumps(error.to_json())


    # def get_param(self, param, default = None):
    #     return bottle.request.params.get(param, default)


    # def get_correlation_id(self):
    #     return bottle.request.query.get('correlation_id')