# -*- coding: utf-8 -*-
"""
    pip_services_rpc.build.DefaultRpcFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DefaultRpcFactory implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services_components.build import Factory
from pip_services_commons.refer import Descriptor
from ..services import HttpEndpoint, StatusRestService, HeartbeatRestService


_Descriptor = Descriptor("pip-services", "factory", "rpc", "default", "1.0")
HttpEndpointDescriptor = Descriptor("pip-services", "endpoint", "http", "*", "1.0")
StatusServiceDescriptor = Descriptor("pip-services", "status-service", "http", "*", "1.0")
HeartbeatServiceDescriptor = Descriptor("pip-services", "heartbeat-service", "http", "*", "1.0")

class DefaultRpcFactory(Factory):
    def __init__(self):
        super(DefaultRpcFactory, self).__init__()
        self.register_as_type(HttpEndpointDescriptor, HttpEndpoint)
        self.register_as_type(StatusServiceDescriptor, StatusRestService)
        self.register_as_type(HeartbeatServiceDescriptor, HeartbeatRestService)