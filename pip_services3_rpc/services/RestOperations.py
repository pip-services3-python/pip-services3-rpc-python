# -*- coding: utf-8 -*-

from abc import ABC
import bottle
import json
import time

from pip_services3_commons.config.IConfigurable import IConfigurable
from pip_services3_commons.config.ConfigParams import ConfigParams
from pip_services3_commons.refer.IReferences import IReferences
from pip_services3_commons.refer.IReferenceable import IReferenceable
from pip_services3_commons.data.FilterParams import FilterParams
from pip_services3_commons.data.PagingParams import PagingParams
from pip_services3_commons.refer.DependencyResolver import DependencyResolver
from pip_services3_commons.errors.BadRequestException import BadRequestException
from pip_services3_commons.errors.UnauthorizedException import UnauthorizedException
from pip_services3_commons.errors.NotFoundException import NotFoundException
from pip_services3_commons.errors.ConflictException import ConflictException
from pip_services3_commons.errors.UnknownException import UnknownException
from .HttpResponseSender import HttpResponseSender
from pip_services3_components.log.CompositeLogger import CompositeLogger
from pip_services3_components.count.CompositeCounters import CompositeCounters


class RestOperations(IConfigurable, IReferenceable, ABC):
    _logger = CompositeLogger()
    _counters = CompositeCounters()
    _dependency_resolver = DependencyResolver()

    def configure(self, config):
        self._dependency_resolver.configure(config)

    def set_references(self, references):
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._dependency_resolver.set_references(references)

    def get_param(self, param, default = None):
        return bottle.request.params.get(param, default)


    def _get_correlation_id(self):
        return bottle.request.query.get('correlation_id')


    def _get_filter_params(self):
        data = dict(bottle.request.query.decode())
        data.pop('correlation_id', None)
        data.pop('skip', None)
        data.pop('take', None)
        data.pop('total', None)
        return FilterParams(data)


    def _get_paging_params(self):
        skip = bottle.request.query.get('skip')
        take = bottle.request.query.get('take')
        total = bottle.request.query.get('total')
        return PagingParams(skip, take, total)


    def _get_data(self):
        data = bottle.request.json
        if isinstance(data, str):
            return json.loads(bottle.request.json)
        elif bottle.request.json:
            return bottle.request.json
        else: 
            return None

    # def _get_correlation_id(self, req=None, res=None):
    #     return req.params.correlation_id

    # def _get_filter_params(self, req=None, res=None):
    #     _res = {}
    #     for key in req.query.keys():
    #         if key not in ['skip', 'take', 'total']:
    #             _res[key] = req.query[key]
    #     return FilterParams.from_value(_res)

    # def _get_paging_params(self, req=None, res=None):
    #     _res = {}
    #     for key in req.query.keys():
    #         if key in ['skip', 'take', 'total']:
    #             _res[key] = req.query[key]

    #     return FilterParams.from_value(_res)

    def _send_result(self, res=None):
        return HttpResponseSender.send_result(res)

    def _send_empty_result(self, res=None):
        return HttpResponseSender.send_empty_result(res)

    def _send_created_result(self, res=None):
        return HttpResponseSender.send_created_result(res)

    def _send_deleted_result(self):
        return HttpResponseSender.send_deleted_result()

    def _send_error(self, error=None):
        HttpResponseSender.send_error(error)

    def _send_bad_request(self, req, message):
        correlation_id = self._get_correlation_id(req)
        error = BadRequestException(correlation_id, 'BAD_REQUEST', message)
        self._send_error(error)

    def _send_unauthorized(self, req, message):
        correlation_id = self._get_correlation_id(req)
        error = UnauthorizedException(correlation_id, 'UNAUTHORIZED', message)
        self._send_error(error)

    def _send_not_found(self, req, message):
        correlation_id = self._get_correlation_id(req)
        error = NotFoundException(correlation_id, 'NOT_FOUND', message)
        self._send_error(error)

    def _send_conflict(self, req, message):
        correlation_id = self._get_correlation_id(req)
        error = ConflictException(correlation_id, 'CONFLICT', message)
        self._send_error(error)

    def _send_session_expired(self, req, message):
        correlation_id = self._get_correlation_id(req)
        error = UnknownException(correlation_id, 'SESSION_EXPIRED', message)
        error.status = 440
        self._send_error(error)

    def _send_internal_error(self, req, message):
        correlation_id = self._get_correlation_id(req)
        error = ConflictException(correlation_id, 'SERVER_UNAVAILABLE', message)
        error.status = 503
        self._send_error(error)

    def invoke(self, operation):
        for attr in dir(self):
            if attr in dir(self):
                return lambda req, res: getattr(self, operation)(req, res)
