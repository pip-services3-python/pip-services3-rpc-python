# -*- coding: utf-8 -*-
"""
    pip_services_rpc.services.StatusRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Status rest service implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import datetime

from pip_services_commons.convert import StringConverter
from pip_services_commons.refer import Descriptor
from pip_services_commons.run import Parameters

from .RestService import RestService

class StatusRestService(RestService):
    _start_time = datetime.datetime.now()
    _references_ = None
    _context_info = None
    _route = "status"

    def __init__(self):
        super(StatusRestService, self).__init__()
        self._dependency_resolver.put("context-info", Descriptor("pip-services", "context-info", "default", "*", "1.0"))

    def configure(self, config):
        super(StatusRestService, self).configure(config)

        self._route = config.get_as_string_with_default("route", self._route)

    def set_references(self, references):
        self._references_ = references

        super(StatusRestService, self).set_references(references)

        self._context_info = self._dependency_resolver.get_one_optional("context-info")

    def register(self):
        self.register_route("GET", self._route, self.status())

    def status(self):
        id = self._context_info.get_context_id() if self._context_info != None else ""
        name = self._context_info.get_name() if self._context_info != None else "unknown"
        description = self._context_info.get_description() if self._context_info != None else ""
        uptime = datetime.datetime.now().time() - self._start_time.time()
        properties = self._context_info.get_properties() if self._context_info != None else ""

        components = []
        if self._references_ != None:
            for locator in self._references_.get_all_locators():
                components.append(locator.__str__)

        status = Parameters.from_tuples("id", id,
                                        "name", name,
                                        "description", description,
                                        "start_time", StringConverter.to_string(self._start_time),
                                        "current_time", StringConverter.to_string(datetime.datetime.now()),
                                        "uptime", uptime,
                                        "properties", properties,
                                        "components", components)
        self.send_result(status)
        # return self.send_result(status)

