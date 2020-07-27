# -*- coding: utf-8 -*-

import netifaces
import datetime
import json
import bottle

from pip_services3_commons.refer.IReferences import IReferences
from pip_services3_commons.refer.Descriptor import Descriptor
from pip_services3_components.info.ContextInfo import ContextInfo
from .HttpResponseDetector import HttpResponseDetector
from .RestService import RestService
from .RestOperations import RestOperations
from .HttpResponseSender import HttpResponseSender

class AboutOperations(RestOperations):
    _context_info = None

    def set_references(self, references):
        super(AboutOperations, self).set_references(references)

        self._context_info = references.get_one_optional(
            Descriptor('pip-services', 'context-info', '*', '*', '*')
        )

    def get_about_operation(self):
        return lambda req, res: self.get_about(req, res)

    def __get_external_addr(self):
        interfaces = netifaces.interfaces()
        addresses = []
        for interface in interfaces:
            if netifaces.AF_INET in netifaces.ifaddresses(interface).keys():
                addr = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr'].split('.')
                mask = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']
                if not ((int(addr[0]) == 10 or int(addr[0]) == 127) or (
                        int(addr[0]) == 172 and 16 <= int(addr[1]) <= 31) or (
                                int(addr[0]) == 192 and int(addr[1]) == 168) or (
                                int(addr[0]) == 100 and 64 <= int(addr[1]) <= 127)) or mask not in ['255.0.0.0',
                                                                                                    '255.240.0.0',
                                                                                                    '255.255.0.0',
                                                                                                    '255.192.0.0']:
                    addresses.append(netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr'])

        return addresses

    def get_network_adresses(self):
        return self.__get_external_addr()

    def get_about(self, req=None, res=None):
        if req is None:
            req = bottle.request
        about = {
            'server': {
                'name': self._context_info.name if not (self._context_info is None) else "unknown",
                'description': self._context_info.description if not (self._context_info is None) else "",
                'properties': self._context_info.properties if not (self._context_info is None) else "",
                'uptime': self._context_info.uptime if not (self._context_info is None) else None,
                'start_time': self._context_info.start_time if not (self._context_info is None) else None,
                'current_time': datetime.datetime.now().isoformat(),
                'protocol': req.method,
                'host': HttpResponseDetector.detect_server_host(req),
                'port': HttpResponseDetector.detect_server_port(req),
                'addresses': self.get_network_adresses(),
                'url': req.url
            },
            'client': {
                'address': HttpResponseDetector.detect_address(req),
                'client': HttpResponseDetector.detect_browser(req),
                'platform': HttpResponseDetector.detect_platform(req),
                'user': req.get_header('user')
            }
        }
        bottle.response.headers['Content-Type'] = 'application/json'
        bottle.response.status = 200

        return self._send_result(about)
