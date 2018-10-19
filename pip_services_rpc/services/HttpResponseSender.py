# -*- coding: utf-8 -*-
"""
    pip_services_rpc.services.HttpResponseSender
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    HttpResponseSender implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json

import bottle
from pip_services_commons.errors import ErrorDescriptionFactory


class HttpResponseSender():
    @staticmethod
    def send_result(self, result):
        bottle.response.headers['Content-Type'] = 'application/json'
        if result == None:
            bottle.response.status = 404
            return
        else:
            bottle.response.status = 200
            return json.dumps(result, default=self._to_json)

    @staticmethod
    def send_created_result(self, result):
        bottle.response.headers['Content-Type'] = 'application/json'
        if result == None:
            bottle.response.status = 404
            return
        else:
            bottle.response.status = 201
            return json.dumps(result, default=self._to_json)

    @staticmethod
    def send_deleted_result(self):
        bottle.response.headers['Content-Type'] = 'application/json'
        bottle.response.status = 204
        return

    @staticmethod
    def send_error(self, error):
        bottle.response.headers['Content-Type'] = 'application/json'
        error = ErrorDescriptionFactory.create(error)
        if error.correlation_id == None:
            error.correlation_id = self.get_correlation_id()
        bottle.response.status = error.status
        return json.dumps(error.to_json())

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

    def get_correlation_id(self):
        return bottle.request.query.get('correlation_id')