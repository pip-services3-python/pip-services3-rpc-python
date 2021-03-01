# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.HttpResponseSender
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    HttpResponseSender implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json

import bottle
from pip_services3_commons.errors import ErrorDescriptionFactory


class HttpResponseSender():
    """
    Helper class that handles HTTP-based responses.
    """

    @staticmethod
    def send_result(result):
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 404
            return
        else:
            bottle.response.status = 200
            return json.dumps(result, default=HttpResponseSender._to_json)

    @staticmethod
    def send_empty_result(result):
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 204
            return json.dumps(result, default=HttpResponseSender._to_json)
        else:
            bottle.response.status = 404
            return

    @staticmethod
    def send_created_result(result):
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 204
            return
        else:
            bottle.response.status = 201
            return json.dumps(result, default=HttpResponseSender._to_json)

    @staticmethod
    def send_deleted_result(result=None):
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 204
            return

        bottle.response.status = 200
        return json.dumps(result, default=HttpResponseSender._to_json) if result else None

    @staticmethod
    def send_error(error):
        """
        Sends error serialized as ErrorDescription object and appropriate HTTP status code. If status code is not defined, it uses 500 status code.

        :param error: an error object to be sent.

        :return: HTTP response status
        """

        error.__dict__.update({'code': 'Undefined', 'status': 500, 'message': 'Unknown error',
                               'name': None, 'details': None,
                               'component': None, 'stack': None, 'cause': None})

        bottle.response.headers['Content-Type'] = 'application/json'
        error = ErrorDescriptionFactory.create(error)
        bottle.response.status = error.status
        return json.dumps(error.to_json())

    @staticmethod
    def _to_json(obj):
        if obj is None:
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

    @staticmethod
    def get_correlation_id(self):
        return bottle.request.query.get('correlation_id')
