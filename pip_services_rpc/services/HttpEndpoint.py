# -*- coding: utf-8 -*-
"""
    pip_services_rpc.services.HttpEndpoint
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Http endpoint implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from threading import Thread

import bottle

from pip_services_commons.config import IConfigurable, ConfigParams
from pip_services_commons.errors import ConnectionException
from pip_services_commons.refer import IReferenceable, DependencyResolver
from pip_services_commons.run import IOpenable
from pip_services_commons.validate import Schema
from pip_services_components.count import CompositeCounters
from pip_services_components.log import CompositeLogger
from .IRegisterable import IRegisterable
from .SimpleServer import SimpleServer
from .HttpResponseSender import HttpResponseSender

from ..connect.HttpConnectionResolver import HttpConnectionResolver


class HttpEndpoint(IOpenable, IConfigurable, IReferenceable):
    _default_config = ConfigParams.from_tuples("connection.protocol", "http",
                                               "connection.host", "0.0.0.0",
                                               "connection.port", 3000,
                                               "connection.request_max_size", 1024 * 1024,
                                               "connection.connect_timeout", 60000,
                                               "connection.debug", True)
    _connection_resolver = HttpConnectionResolver()
    #_dependency_resolver = DependencyResolver()
    _logger = CompositeLogger()
    _counters = CompositeCounters()

    _service = None
    _server = None
    #_resource = None
    _uri = None
    _registrations = []


    def configure(self, config):
        config = config.set_defaults(self._default_config)
        self._connection_resolver.configure(config)

    def set_references(self, references):
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._connection_resolver.set_references(references)

    def is_opened(self):
        return self._server != None

    def open(self, correlation_id):
        if self.is_opened():
            return

        connection = self._connection_resolver.resolve(correlation_id)

        self._uri = connection.get_uri()

        # Create instance of bottle application
        self._service = bottle.Bottle(catchall = True, autojson = True)

        # Enable CORS requests
        self._service.add_hook('after_request', self._enable_cors)
        self._service.route('/', 'OPTIONS', self._options_handler)
        self._service.route('/<path:path>', 'OPTIONS', self._options_handler)
        def start_server():
            self._service.run(server = self._server, debug = False)

        # Starting service
        try:
            self._server = SimpleServer(host = connection.get_host(), port = connection.get_port())

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
        try:
            if self._server != None:
                self._server.shutdown()
                self._logger.debug(correlation_id, "Closed REST service at %s", self._uri)

            self._server = None
            self._uri = None
        except Exception as ex:
            self._logger.warn(correlation_id, "Failed while closing REST service: " + str(ex))

    def register(self, registration):
        self._registrations.append(registration)

    def unregister(self, registration):
        self._registrations.remove(registration)

    def perform_registrations(self):
        for registration in self._registrations:
            registration.register()

    def register_route(self, method, route, schema, handler):
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

        self._service.route(route, method, wrapper)

    def get_data(self):
         return bottle.request.json

    def _enable_cors(self):
        bottle.response.headers['Access-Control-Allow-Origin'] = '*'
        bottle.response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
        bottle.response.headers['Access-Control-Allow-Headers'] = 'Authorization, Origin, Accept, Content-Type, X-Requested-With'

    def _options_handler(self, ath = None):
        return