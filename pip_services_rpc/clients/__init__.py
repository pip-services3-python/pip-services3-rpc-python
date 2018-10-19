# -*- coding: utf-8 -*-
"""
    pip_services_rpc.clients.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Clients module implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ['CommandableHttpClient', 'DirectClient', 'RestClient']

from .CommandableHttpClient import CommandableHttpClient
from .DirectClient import DirectClient
from .RestClient import RestClient