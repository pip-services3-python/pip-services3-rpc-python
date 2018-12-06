# -*- coding: utf-8 -*-
"""
    pip_services_rpc.rest.CommandableHttpService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Commandable HTTP service implementation
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services_commons.refer import IReferences
from pip_services_commons.commands import ICommandable, CommandSet
from pip_services_commons.run import Parameters

from .RestService import RestService

class CommandableHttpService(RestService):
    _name = None
    _command_set = None

    def __init__(self, name):
        super(CommandableHttpService, self).__init__()
        self._name = name
        self._dependency_resolver.put('controller', 'none')

    def _get_handler(self, command):
        def handler():
            params = self.get_data()
            correlation_id = params['correlation_id'] if 'correlation_id' in params else None
            args = Parameters.from_value(params)

            timing = self._instrument(correlation_id, self._name + '.' + command.get_name())
            try:
                result = command.execute(correlation_id, args)
                return self.send_result(result)
            finally:
                timing.end_timing()

        return handler

    def add_route(self):
        controller = self._dependency_resolver.get_one_required('controller')
        if not isinstance(controller, ICommandable):
            raise Exception("Controller has to implement ICommandable interface")
        self._command_set = controller.get_command_set()

        for command in self._command_set.get_commands():
            route = '/' + self._name + '/' + command.get_name()
            self.register_route('POST', route, None, self._get_handler(command))