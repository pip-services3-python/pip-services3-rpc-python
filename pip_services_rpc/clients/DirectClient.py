# -*- coding: utf-8 -*-
"""
    pip_services_rpc.clients.DirectClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Direct client implementation
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services_commons.run import IOpenable
from pip_services_commons.config import ConfigParams, IConfigurable
from pip_services_commons.refer import Descriptor, IReferences, IReferenceable, DependencyResolver
from pip_services_components.log import CompositeLogger
from pip_services_components.count import CompositeCounters
from pip_services_commons.errors import ConnectionException

class DirectClient(IConfigurable, IReferenceable, IOpenable):
    _controller = None
    _opened = True
    _logger = None
    _counters = None
    _dependency_resolver = None

    def __init__(self):
        self._logger = CompositeLogger()
        self._counters = CompositeCounters()
        self._dependency_resolver = DependencyResolver()
        self._dependency_resolver.put('controller', 'none')

    def configure(self, config):
        self._dependency_resolver.configure(config)

    def set_references(self, references):
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._dependency_resolver.set_references(references)
        self._controller = self._dependency_resolver.get_one_required('controller')

    def _instrument(self, correlation_id, name):
        self._logger.trace(correlation_id, "Executing " + name + " method")
        return self._counters.begin_timing(name + ".call_time")

    def is_opened(self):
        return self._opened

    def open(self, correlation_id):
        if self._opened:
            return
        
        if self._controller == None:
            raise ConnectionException(correlation_id, 'NO_CONTROLLER', 'Controller references is missing')

        self._opened = True
        self._logger.info(correlation_id, 'Opened direct client')

    def close(self, correlation_id):
        if self._opened:
            self._logger.info(correlation_id, 'Closed direct client')

        self._opened = False

