# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.connect.HttpConnectionResolver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    HttpConnectionResolver implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from urllib.parse import urlparse

from pip_services3_commons.config import IConfigurable
from pip_services3_commons.errors import ConfigException
from pip_services3_commons.refer import IReferenceable
from pip_services3_components.connect import ConnectionResolver
from pip_services3_components.auth.CredentialParams import CredentialParams
from pip_services3_components.auth.CredentialResolver import CredentialResolver


class HttpConnectionResolver(IReferenceable, IConfigurable):
    """
    Helper class to retrieve connections for HTTP-based services abd clients. In addition to regular functions of
    ConnectionResolver is able to parse http:// URIs and validate connection parameters before returning them.

    ### Configuration parameters ###
        - connection:
            - discovery_key:               (optional) a key to retrieve the connection from IDiscovery
            - ...                          other connection parameters
        - connections:                   alternative to connection
            - [connection params 1]:       first connection parameters
            -  ...
            - [connection params N]:       Nth connection parameters
            -  ...

    ### References ###
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services3_components.connect.IDiscovery.IDiscovery>` services to resolve connection

    Example:
    
    .. code-block:: python

          config = ConfigParams.from_tuples("connection.host", "10.1.1.100","connection.port", 8080)
          connectionResolver = HttpConnectionResolver()
          connectionResolver.configure(config)
          connectionResolver.set_references(references)
          params = connectionResolver.resolve("123")
    """

    # Create connection resolver.
    _connection_resolver = None

    # The base credential resolver.
    _credential_resolver = None

    def __init__(self):
        self._connection_resolver = ConnectionResolver()
        self._credential_resolver = CredentialResolver()

    def configure(self, config):
        """
        Configures component by passing configuration parameters.
        :param config: configuration parameters to be set.
        """
        self._connection_resolver.configure(config)
        self._credential_resolver.configure(config)

    def set_references(self, references):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._connection_resolver.set_references(references)
        self._credential_resolver.set_references(references)

    def __validate_connection(self, correlation_id, connection, credential=None):

        # Sometimes when we use https we are on an internal network and do not want to have to deal with security.
        # When we need a https connection and we don't want to pass credentials, flag is 'credential.internal_network',
        # this flag just has to be present and non null for this functionality to work.
        if connection is None:
            raise ConfigException(correlation_id, "NO_CONNECTION", "HTTP connection is not set")
        uri = connection.get_uri()

        if uri is not None:
            return None

        protocol = connection.get_protocol("http")
        if protocol != "http" and 'https' != protocol:
            raise ConfigException(correlation_id,
                                  "WRONG_PROTOCOL",
                                  "Protocol is not supported by REST connection") \
                .with_details("protocol", protocol)

        host = connection.get_host()
        if host is None:
            raise ConfigException(correlation_id, "NO_HOST", "Connection host is not set")

        port = connection.get_port()
        if port == 0:
            raise ConfigException(correlation_id, "NO_PORT", "Connection port is not set")

        # Check HTTPS credentials
        if protocol == 'https':
            # Check for credential
            if credential is None:
                raise ConfigException(
                    correlation_id, 'NO_CREDENTIAL',
                    'SSL certificates are not configured for HTTPS protocol')
            else:
                # Sometimes when we use https we are on an internal network and do not want to have to deal with
                # security. When we need a https connection and we don't want to pass credentials,
                # flag is 'credential.internal_network', this flag just has to be present and non null for this
                # functionality to work.
                if credential.get_as_nullable_string('internal_network') is None:
                    if credential.get_as_nullable_string('ssl_key_file') is None:
                        raise ConfigException(
                            correlation_id, 'NO_SSL_KEY_FILE',
                            'SSL key file is not configured in credentials')
                    elif credential.get_as_nullable_string('ssl_crt_file') is None:
                        raise ConfigException(
                            correlation_id, 'NO_SSL_CRT_FILE',
                            'SSL crt file is not configured in credentials')
        return None

    def __update_connection(self, connection, credential=None):
        if connection is None:
            return

        uri = connection.get_uri()

        if uri is None or uri == "":

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

        if connection.get_protocol() == 'https':
            _cred_internal = connection.get_as_nullable_string('internal_network')
            if _cred_internal is None:
                _cred_internal = credential
            else:
                _cred_internal = CredentialParams()
            connection.add_section('credential', _cred_internal)
        else:
            connection.add_section('credential', CredentialParams())

    def resolve(self, correlation_id):
        """
        Resolves a single component connection. If connections are configured to be retrieved from Discovery service
        it finds a IDiscovery and resolves the connection there.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :return: resolved connection.
        """

        connection = self._connection_resolver.resolve(correlation_id)
        credential = self._credential_resolver.lookup(correlation_id)
        self.__validate_connection(correlation_id, connection, credential)
        self.__update_connection(connection, credential)

        connection.update(credential)

        return connection

    def resolve_all(self, correlation_id):
        """
        Resolves all component connection. If connections are configured to be retrieved from Discovery service it finds a IDiscovery and resolves the connection there.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :return: resolved connections.
        """

        connections = self._connection_resolver.resolve_all(correlation_id)
        for connection in connections:
            self.__validate_connection(correlation_id, connection)
            self.__update_connection(connection)

        return connections

    def register(self, correlation_id):
        """
        Registers the given connection in all referenced discovery services. This method can be used for dynamic service discovery.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        connection = self._connection_resolver.resolve(correlation_id)
        self.__validate_connection(correlation_id, connection)
        self._connection_resolver.register(correlation_id, connection)
