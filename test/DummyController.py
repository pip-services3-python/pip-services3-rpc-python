# -*- coding: utf-8 -*-
"""
    test.DummyController
    ~~~~~~~~~~~~~~~~~~~~
    
    Dummy controller object
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import threading

from pip_services3_commons.data import FilterParams, PagingParams, DataPage, IdGenerator
from pip_services3_commons.commands import ICommandable
from pip_services3_commons.errors import BadRequestException

from .IDummyController import IDummyController
from .DummyCommandSet import DummyCommandSet

class DummyController(IDummyController, ICommandable):
    _lock = None
    _items = None
    _command_set = None

    def __init__(self):
        self._lock = threading.Lock()
        self._items = []


    def get_command_set(self):
        if self._command_set is None:
            self._command_set = DummyCommandSet(self)
        return self._command_set


    def get_page_by_filter(self, correlation_id, filters, paging):
        filters = filters if not (filters is None) else FilterParams()
        key = filters.get_as_nullable_string("key")
        
        paging = paging if not (paging is None) else PagingParams()
        skip = paging.get_skip(0)
        take = paging.get_take(100)
        
        result = []
        self._lock.acquire()
        try:
            for item in self._items:
                if not (key is None) and key != item['key']:
                    continue
                
                skip -= 1
                if skip >= 0: continue 
                
                take -= 1
                if take < 0: break
                
                result.append(item)
        finally:
            self._lock.release()

        return DataPage(result)


    def get_one_by_id(self, correlation_id, id):
        self._lock.acquire()
        try:
            for item in self._items:
                if item['id'] == id:
                    return item
        finally:
            self._lock.release()

        return None

    def create(self, correlation_id, item):
        self._lock.acquire()
        try:
            if 'id' not in item or item['id'] is None:
                item['id'] = IdGenerator.next_long()

            self._items.append(item)
        finally:
            self._lock.release()
        
        return item

    def update(self, correlation_id, new_item):
        self._lock.acquire()
        try:
            for index in range(len(self._items)):
                item = self._items[index]
                if item['id'] == new_item['id']:
                    self._items[index] = new_item
                    return new_item
        finally:
            self._lock.release()

        return None

    def delete_by_id(self, correlation_id, id):
        self._lock.acquire()
        try:
            for index in range(len(self._items)):
                item = self._items[index]
                if item['id'] == id:
                    del self._items[index]
                    return item
        finally:
            self._lock.release()

        return None
