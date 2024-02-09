from dataclasses import dataclass
from typing import Any
import unittest
from pydantic import GetCoreSchemaHandler, TypeAdapter
from protobase import traits
from protobase.core import Obj

from pydantic_core import core_schema


# traits.Schema
# rxmodels


class TestPydanticCompat(unittest.TestCase):
    class MyObj(Obj, *traits.Common):
        alpha: int
        beta: int

        @classmethod
        def __get_pydantic_core_schema__(
            cls,
            source: type[Any],
            handler: GetCoreSchemaHandler,
        ) -> core_schema.CoreSchema:

            fields = {}

            return core_schema.typed_dict_schema()

    def test_serialization(self):
        obj = self.MyObj(alpha=1, beta=2)
        adapter = TypeAdapter(TestPydanticCompat.MyObj)
