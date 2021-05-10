# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.HttpResponseSender
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    HttpResponseSender implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json
from typing import Any, Optional

import bottle
from pip_services3_commons.errors import ErrorDescriptionFactory


class HttpResponseSender:
    """
    Helper class that handles HTTP-based responses.
    """

    @staticmethod
    def send_result(result: Any) -> Optional[str]:
        """
        Creates a callback function that sends result as JSON object.
        That callack function call be called directly or passed
        as a parameter to business logic components.

        If object is not null it returns 200 status code.
        For null results it returns 204 status code.
        If error occur it sends ErrorDescription with approproate status code.

        :param result: an execution result
        :returns: JSON text response
        """
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 404
            return
        else:
            bottle.response.status = 200
            return json.dumps(result, default=HttpResponseSender._to_json)

    @staticmethod
    def send_empty_result(result: Any = None) -> Optional[str]:
        """
        Creates a callback function that sends an empty result with 204 status code.
        If error occur it sends ErrorDescription with approproate status code.

        :param result:
        :returns: JSON text response

        """
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 204
            return json.dumps(result, default=HttpResponseSender._to_json)
        else:
            bottle.response.status = 404
            return

    @staticmethod
    def send_created_result(result: Any) -> Optional[str]:
        """
        Creates a callback function that sends newly created object as JSON.
        That callack function call be called directly or passed
        as a parameter to business logic components.

        If object is not null it returns 201 status code.
        For null results it returns 204 status code.
        If error occur it sends ErrorDescription with approproate status code.

        :param result: an execution result or a promise with execution result
        :returns: JSON text response

        """
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 204
            return
        else:
            bottle.response.status = 201
            return json.dumps(result, default=HttpResponseSender._to_json)

    @staticmethod
    def send_deleted_result(result: Any = None) -> Optional[str]:
        """
        Creates a callback function that sends newly created object as JSON.
        That callack function call be called directly or passed
        as a parameter to business logic components.

        If object is not null it returns 201 status code.
        For null results it returns 204 status code.
        If error occur it sends ErrorDescription with approproate status code.

        :param result: an execution result or a promise with execution result
        :returns: JSON text response

        """
        bottle.response.headers['Content-Type'] = 'application/json'
        if result is None:
            bottle.response.status = 204
            return

        bottle.response.status = 200
        return json.dumps(result, default=HttpResponseSender._to_json) if result else None

    @staticmethod
    def send_error(error: Any) -> str:
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
                item = HttpResponseSender._to_json(item)
                result.append(item)
            return result

        if isinstance(obj, dict):
            result = {}
            for (k, v) in obj.items():
                v = HttpResponseSender._to_json(v)
                result[k] = v
            return result

        if hasattr(obj, 'to_json'):
            return obj.to_json()
        if hasattr(obj, '__dict__'):
            attribs = dict(obj.__dict__)
            dict_obj = {}
            
            for key in attribs.keys():
                if not (key.endswith('__') and key.startswith('__')):
                    dict_obj[key] = attribs[key]

            return HttpResponseSender._to_json(dict_obj)
        return obj
