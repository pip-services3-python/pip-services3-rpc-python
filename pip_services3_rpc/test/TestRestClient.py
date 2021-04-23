# -*- coding: utf-8 -*-

from pip_services3_rpc.clients import RestClient


class TestRestClient(RestClient):
    """
    REST client used for automated testing.
    """

    def __init__(self, base_route):
        super(TestRestClient, self).__init__()
        self._base_route = base_route

    def call(self, method, route, correlation_id=None, params=None, data=None):
        """
        Calls a remote method via HTTP/REST protocol.

        :param method: HTTP method: "get", "head", "post", "put", "delete"
        :param route: a command route. Base route will be added to this route
        :param correlation_id: (optional) transaction id to trace execution through call chain.
        :param params: (optional) query parameters.
        :param data: (optional) body object.
        :returns: a result object.
        """
        return super(TestRestClient, self).call(method, route, correlation_id, params, data)
