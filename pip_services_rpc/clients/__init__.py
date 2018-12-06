# -*- coding: utf-8 -*-
"""
    pip_services_rpc.rest.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Net rest module initialization
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [ 'DirectClient', 'RestClient', 'CommandableHttpClient' ]

from .DirectClient import DirectClient
from .RestClient import RestClient
from .CommandableHttpClient import CommandableHttpClient
