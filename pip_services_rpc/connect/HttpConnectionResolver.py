# -*- coding: utf-8 -*-
"""
    pip_services_rpc.connect.HttpConnectionResolver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    HttpConnectionResolver implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from urllib.parse import urlparse

from pip_services_commons.config import IConfigurable
from pip_services_commons.errors import ConfigException
from pip_services_commons.refer import IReferenceable
from pip_services_components.connect import ConnectionResolver


class HttpConnectionResolver(IReferenceable, IConfigurable):
    _connection_resolver = ConnectionResolver()

    def configure(self, config):
        self._connection_resolver.configure(config)

    def set_references(self, references):
        self._connection_resolver.set_references(references)

    def validate_connection(self, correlation_id, connection):
        if connection == None:
            return ConfigException(correlation_id, "NO_CONNECTION", "HTTP connection is not set")

        uri = connection.get_uri()
        if uri == None:
            return None

        protocol = connection.get_protocol("http")
        if protocol != "http":
            return ConfigException(correlation_id,
                                   "WRONG_PROTOCOL",
                                   "Protocol is not supported by REST connection")\
                .with_details("protocol", protocol)

        host = connection.get_host()
        if host == None:
            return ConfigException(correlation_id, "NO_HOST", "Connection host is not set")

        port = connection.get_port()
        if port == 0:
            return ConfigException(correlation_id, "NO_PORT", "Connection port is not set")

    def update_connection(self, connection):
        if connection == None:
            return

        uri = connection.get_uri()

        if uri == None or uri == "":
            protocol = connection.get_protocol("http")
            host = connection.get_host()
            port = connection.get_port()

            uri = protocol + "://" + host
            if port != 0:
                uri = uri + ":" + str(port)
            connection.set_uri(uri)

        else:
            address = urlparse(uri)
            connection.set_protocol(address.scheme)
            connection.set_host(address.hostname)
            connection.set_port(address.port)

    def resolve(self, correlation_id):
        connection = self._connection_resolver.resolve(correlation_id)
        self.validate_connection(correlation_id, connection)
        self.update_connection(connection)
        return connection

    def resolve_all(self, correlation_id):
        connections = self._connection_resolver.resolve_all(correlation_id)
        for connection in connections:
            self.validate_connection(correlation_id, connection)
            self.update_connection(connection)

        return connections

    def register(self, correlation_id):
        connection = self._connection_resolver.resolve(correlation_id)
        self.validate_connection(correlation_id, connection)
        self._connection_resolver.register(correlation_id, connection)



