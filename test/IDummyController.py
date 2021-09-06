# -*- coding: utf-8 -*-
"""
    test.IDummyController
    ~~~~~~~~~~~~~~~~~~~~~
    
    Interface for dummy controllers
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.data import FilterParams, PagingParams, DataPage

from test import Dummy


class IDummyController:
    def get_page_by_filter(self, correlation_id: Optional[str], filter: FilterParams, paging: PagingParams) -> DataPage:
        raise NotImplementedError('Method from interface definition')

    def get_one_by_id(self, correlation_id: Optional[str], id: str) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def create(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def update(self, correlation_id: Optional[str], new_item: Dummy) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def delete_by_id(self, correlation_id: Optional[str], id: str) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def check_correlation_id(self, correlation_id: Optional[str]) -> str:
        raise NotImplementedError('Method from interface definition')
