# -*- coding: utf-8 -*-
"""
    test.DummyCommandSet
    ~~~~~~~~~~~~~~~~~~~~

    Dummy command set

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services3_commons.commands import Command, CommandSet, ICommand
from pip_services3_commons.convert import TypeCode
from pip_services3_commons.data import FilterParams, PagingParams
from pip_services3_commons.run import Parameters
from pip_services3_commons.validate import ObjectSchema, FilterParamsSchema, PagingParamsSchema

from test import IDummyController, Dummy
from test.DummySchema import DummySchema


class DummyCommandSet(CommandSet):
    _controller: IDummyController

    def __init__(self, controller):
        super(DummyCommandSet, self).__init__()

        self._controller = controller

        self.add_command(self._make_get_page_by_filter_command())
        self.add_command(self._make_get_one_by_id_command())
        self.add_command(self._make_create_command())
        self.add_command(self._make_update_command())
        self.add_command(self._make_delete_by_id_command())
        self.add_command(self._make_check_correlation_id())

    def _make_get_page_by_filter_command(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters):
            filter = FilterParams.from_value(args.get("filter"))
            paging = PagingParams.from_value(args.get("paging"))
            return self._controller.get_page_by_filter(correlation_id, filter, paging)

        return Command(
            "get_dummies",
            ObjectSchema(True).with_optional_property("filter", FilterParamsSchema()).with_optional_property(
                "paging", PagingParamsSchema()),
            handler
        )

    def _make_get_one_by_id_command(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters):
            id = args.get_as_string("dummy_id")
            return self._controller.get_one_by_id(correlation_id, id)

        return Command(
            "get_dummy_by_id",
            ObjectSchema(True).with_required_property("dummy_id", TypeCode.String), handler)

    def _make_create_command(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters):
            entity = args.get("dummy")
            if isinstance(entity, dict):
                entity = Dummy(**entity)
            return self._controller.create(correlation_id, entity)

        return Command(
            "create_dummy",
            ObjectSchema(True).with_required_property("dummy", DummySchema()),
            handler
        )

    def _make_update_command(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters):
            entity = args.get("dummy")
            if isinstance(entity, dict):
                entity = Dummy(**entity)
            return self._controller.update(correlation_id, entity)

        return Command(
            "update_dummy",
            ObjectSchema(True).with_required_property("dummy", DummySchema()),
            handler
        )

    def _make_delete_by_id_command(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters):
            id = args.get_as_string("dummy_id")
            return self._controller.delete_by_id(correlation_id, id)

        return Command(
            "delete_dummy",
            ObjectSchema(True).with_required_property("dummy_id", TypeCode.String),
            handler
        )

    def _make_check_correlation_id(self) -> ICommand:
        def handler(correlation_id: Optional[str], args: Parameters):
            value = self._controller.check_correlation_id(correlation_id)
            return {'correlation_id': value}

        return Command(
            "check_correlation_id",
            ObjectSchema(True),
            handler
        )
