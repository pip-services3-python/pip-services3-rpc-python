# -*- coding: utf-8 -*-
"""
    test.DummyCommandSet
    ~~~~~~~~~~~~~~~~~~~~
    
    Dummy command set
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.data import FilterParams, PagingParams
from pip_services3_commons.commands import Command, CommandSet

from .IDummyController import IDummyController

class DummyCommandSet(CommandSet):
    _controller = None

    def __init__(self, controller):
        super(DummyCommandSet, self).__init__()

        self._controller = controller

        self.add_command(self._make_get_page_by_filter_command())
        self.add_command(self._make_get_one_by_id_command())
        self.add_command(self._make_create_command())
        self.add_command(self._make_update_command())
        self.add_command(self._make_delete_by_id_command())

    def _make_get_page_by_filter_command(self):
        def handler(correlation_id, args):
            filter = FilterParams.from_value(args.get("filter"))
            paging = PagingParams.from_value(args.get("paging"))
            return self._controller.get_page_by_filter(correlation_id, filter, paging)

        return Command(
            "get_dummies",
            None,
            handler
        )

    def _make_get_one_by_id_command(self):
        def handler(correlation_id, args):
            id = args.get_as_string("dummy_id")
            return self._controller.get_one_by_id(correlation_id, id)

        return Command(
            "get_dummy_by_id",
            None,
            handler
        )

    def _make_create_command(self):
        def handler(correlation_id, args):
            entity = args.get("dummy")
            return self._controller.create(correlation_id, entity)

        return Command(
            "create_dummy",
            None,
            handler
        )

    def _make_update_command(self):
        def handler(correlation_id, args):
            entity = args.get("dummy")
            return self._controller.update(correlation_id, entity)

        return Command(
            "update_dummy",
            None,
            handler
        )

    def _make_delete_by_id_command(self):
        def handler(correlation_id, args):
            id = args.get_as_string("dummy_id")
            return self._controller.delete_by_id(correlation_id, id)

        return Command(
            "delete_dummy_by_id",
            None,
            handler
        )
