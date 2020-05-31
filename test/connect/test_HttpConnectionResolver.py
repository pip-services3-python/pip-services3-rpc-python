# -*- coding: utf-8 -*-
"""
    tests.connect.test_HttpConnectionResolver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services3_commons.config import ConfigParams
from pip_services3_rpc.connect import HttpConnectionResolver
from pip_services3_commons.errors.ConfigException import ConfigException


class TestHttpConnectionResolver:

    def test_connection_params(self):
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples("connection.protocol", "http",
                                                               "connection.host", "somewhere.com",
                                                               "connection.port", 123))
        connection = connection_resolver.resolve(None)

        assert connection.get_protocol() == "http"
        assert connection.get_host() == "somewhere.com"
        assert connection.get_port() == 123
        assert connection.get_uri() == "http://somewhere.com:123"

    def test_connection_uri(self):
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples("connection.uri", "https://somewhere.com:123"))

        connection = connection_resolver.resolve(None)

        assert connection.get_protocol() == "https"
        assert connection.get_host() == "somewhere.com"
        assert connection.get_port() == 123
        assert connection.get_uri() == "https://somewhere.com:123"


class TestHttpsCredentials:

    def test_https_with_credentials_connection_params(self):
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https",
            "credential.ssl_key_file", "ssl_key_file",
            "credential.ssl_crt_file", "ssl_crt_file",
        ))

        connection = connection_resolver.resolve(None)

        assert 'https' == connection.get_protocol()
        assert 'somewhere.com' == connection.get_host()
        assert 123 == connection.get_port()
        assert 'https://somewhere.com:123' == connection.get_uri()
        assert 'ssl_key_file' == connection.get('credential.ssl_key_file')
        assert 'ssl_crt_file' == connection.get('credential.ssl_crt_file')

    def test_https_with_no_credentials_connection_params(self):
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https",
            "credential.internal_network", "internal_network"
        ))
        connection = connection_resolver.resolve(None)

        assert 'https' == connection.get_protocol()
        assert 'somewhere.com' == connection.get_host()
        assert 123 == connection.get_port()
        assert 'https://somewhere.com:123' == connection.get_uri()
        assert connection.get('credential.internal_network')

    def test_https_with_missing_credentials_connection_params(self):
        # Section missing
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https"
        ))
        print('Test - section missing')
        try:
            connection_resolver.resolve(None)
        except ConfigException as err:
            assert err.code == 'NO_SSL_KEY_FILE'
            assert err.name == 'NO_SSL_KEY_FILE'
            assert err.message == 'SSL key file is not configured in credentials'
            assert err.category == 'Misconfiguration'

        # ssl_crt_file missing
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https",
            "credential.ssl_key_file", "ssl_key_file"
        ))

        print('Test - ssl_crt_file missing')
        try:
            connection_resolver.resolve(None)
        except ConfigException as err:
            assert err.code == 'NO_SSL_CRT_FILE'
            assert err.name == 'NO_SSL_CRT_FILE'
            assert err.message == 'SSL crt file is not configured in credentials'
            assert err.category == 'Misconfiguration'

        # ssl_key_file missing
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https",
            "credential.ssl_crt_file", "ssl_crt_file"
        ))
        print('Test - ssl_key_file missing')
        try:
            connection_resolver.resolve(None)
        except ConfigException as err:
            assert err.code == 'NO_SSL_KEY_FILE'
            assert err.name == 'NO_SSL_KEY_FILE'
            assert err.message == 'SSL key file is not configured in credentials'
            assert err.category == 'Misconfiguration'

        # ssl_key_file, ssl_crt_file present
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples(
            "connection.host", "somewhere.com",
            "connection.port", 123,
            "connection.protocol", "https",
            "credential.ssl_key_file", "ssl_key_file",
            "credential.ssl_crt_file", "ssl_crt_file"
        ))
        print('Test - ssl_key_file,  ssl_crt_file present')
        connection = connection_resolver.resolve(None)

        assert 'https' == connection.get_protocol()
        assert 'somewhere.com' == connection.get_host()
        assert 123 == connection.get_port()
        assert 'https://somewhere.com:123' == connection.get_uri()
        assert 'ssl_key_file' == connection.get('credential.ssl_key_file')
        assert 'ssl_crt_file' == connection.get('credential.ssl_crt_file')
