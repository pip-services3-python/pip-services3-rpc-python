# -*- coding: utf-8 -*-

import datetime
import pytz
import bottle
import json

from pip_services3_commons.run import Parameters
from pip_services3_components.info.ContextInfo import ContextInfo
from pip_services3_commons.refer.Descriptor import Descriptor
from pip_services3_commons.refer.IReferences import IReferences
from pip_services3_commons.convert.StringConverter import StringConverter

from .RestService import RestService
from .RestOperations import RestOperations


class StatusOperations(RestOperations):
    _start_time = datetime.datetime.now()
    _references2 = None
    _context_info = None

    def __init__(self):
        super(StatusOperations, self).__init__()
        self._dependency_resolver.put((
            'context-info',
            Descriptor('pip-services', 'context-info', 'default', '*', '1.0')
        ))

    def set_references(self, references):
        '''
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        '''

        self._references2 = references
        super(StatusOperations, self).set_references(references)

        self._context_info = self._dependency_resolver.get_one_optional('context-info')

    def get_status_operation(self):
        return lambda req, res: self.status(req, res)

    def status(self, req=None, res=None):
        '''
        Handles status requests

        :param req: an HTTP request
        :param res: an HTTP response
        '''
        _id = self._context_info.context_id if not (self._context_info is None) else ''
        name = self._context_info.name if not (self._context_info is None) else 'unknown'
        description = self._context_info.description if not (self._context_info is None) else ''
        uptime = datetime.datetime.fromtimestamp((
                datetime.datetime.now().timestamp() - self._start_time.timestamp()),
                                                 pytz.utc).strftime("%H:%M:%S")
        properties = self._context_info.properties if not (self._context_info is None) else ''

        components = []
        if self._references2 is not None:
            for locator in self._references2.get_all_locators():
                components.append(locator.__str__)

        status = {'id': _id,
                  'name': name,
                  'description': description,
                  'start_time': StringConverter.to_string(self._start_time),
                  'current_time': StringConverter.to_string(datetime.datetime.now()),
                  'uptime': uptime,
                  'properties': properties,
                  'components': components}
        bottle.response.headers['Content-Type'] = 'application/json'
        bottle.response.status = 200
        return json.dumps(status, default=RestService._to_json)
