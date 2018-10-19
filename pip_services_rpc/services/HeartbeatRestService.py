# -*- coding: utf-8 -*-
"""
    pip_services_rpc.services.HeartbeatRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Heartbeat rest service implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import datetime

from pip_services_commons.convert import StringConverter

from .RestService import RestService

class HeartbeatRestService(RestService):
    _route = "heartbeat"

    def __init__(self):
        super(HeartbeatRestService, self).__init__()

    def configure(self, config):
        super(HeartbeatRestService, self).configure(config)
        self._route = config.get_as_string_with_default("route", self._route)

    def register(self):
        self.register_route("GET", self._route, self.heartbeat())

    def heartbeat(self):
        result = StringConverter.to_string(datetime.datetime.now())
        return self.send_result(result)


