# -*- coding: utf-8 -*-
"""
    test.Dummy
    ~~~~~~~~~~
    
    Dummy data object
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import List

from pip_services3_commons.data import IStringIdentifiable

from test.SubDummy import SubDummy


class Dummy(IStringIdentifiable):
    def __init__(self, id: str = None, key: str = None, content: str = None, array: List[SubDummy] = None):
        self.id = id
        self.key = key
        self.content = content
        self.array = array

    def to_json(self):
        return {
            'id': self.id,
            'key': self.key,
            'content': self.content,
            'array': [item.__dict__ for item in self.array]
        }

    @staticmethod
    def from_json(data: dict):
        id = data.get('id')
        key = data.get('key')
        content = data.get('content')
        array = []
        for item in data.get('array'):
            array.append(SubDummy(**item))

        return Dummy(id, key, content, array)
