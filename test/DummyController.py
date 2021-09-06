# -*- coding: utf-8 -*-
"""
    test.DummyController
    ~~~~~~~~~~~~~~~~~~~~
    
    Dummy controller object
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import threading
from typing import List, Optional

from pip_services3_commons.commands import ICommandable, CommandSet
from pip_services3_commons.data import FilterParams, PagingParams, DataPage, IdGenerator

from . import Dummy
from .DummyCommandSet import DummyCommandSet
from .IDummyController import IDummyController


class DummyController(IDummyController, ICommandable):

    def __init__(self):
        self.__lock = threading.Lock()
        self.__items: List[Dummy] = []
        self.__command_set: CommandSet = None

    def get_command_set(self):
        if self.__command_set is None:
            self.__command_set = DummyCommandSet(self)
        return self.__command_set

    def get_page_by_filter(self, correlation_id: Optional[str], filter: FilterParams, paging: PagingParams) -> DataPage:
        filters = filter if filter is not None else FilterParams()
        key = filters.get_as_nullable_string("key")

        paging = paging if not (paging is None) else PagingParams()
        skip = paging.get_skip(0)
        take = paging.get_take(100)

        result = []
        self.__lock.acquire()
        try:
            for item in self.__items:
                if not (key is None) and key != item.key:
                    continue

                skip -= 1
                if skip >= 0: continue

                take -= 1
                if take < 0: break

                result.append(item)
        finally:
            self.__lock.release()

        return DataPage(result)

    def get_one_by_id(self, correlation_id: Optional[str], id: str) -> Optional[Dummy]:
        self.__lock.acquire()
        try:
            for item in self.__items:
                if item.id == id:
                    return item
        finally:
            self.__lock.release()

        return None

    def create(self, correlation_id: Optional[str], item: Dummy) -> Dummy:
        self.__lock.acquire()
        try:
            if item.id is None:
                item.id = IdGenerator.next_long()

            self.__items.append(item)
        finally:
            self.__lock.release()

        return item

    def update(self, correlation_id: Optional[str], new_item: Dummy) -> Optional[Dummy]:
        self.__lock.acquire()
        try:
            for index in range(len(self.__items)):
                item = self.__items[index]
                if item.id == new_item.id:
                    self.__items[index] = new_item
                    return new_item
        finally:
            self.__lock.release()

        return None

    def delete_by_id(self, correlation_id: Optional[str], id: str) -> Optional[Dummy]:
        self.__lock.acquire()
        try:
            for index in range(len(self.__items)):
                item = self.__items[index]
                if item.id == id:
                    del self.__items[index]
                    return item
        finally:
            self.__lock.release()

        return None

    def check_correlation_id(self, correlation_id: Optional[str]) -> str:
        return correlation_id
