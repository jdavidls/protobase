from typing import Self
from protobase.core import Trait, fields_of, impl, protomethod
from protobase.utils import compile_function


class Eq(Trait):
    """
    A trait that enables equality operators (__eq__, __ne__) based on
    the fields of a proto object.

    Example:

        >>> from protobase.core import Base
        >>> from protobase.trait import Eq
        >>>
        >>> class Point(Base, Eq):
        ...     x: int
        ...     y: int
        ...
        >>> p1 = Point(x=1, y=2)
        >>> p2 = Point(x=2, y=1)
        >>> p3 = Point(x=1, y=2)
        >>> p1 == p2
        False
        >>> p1 == p3
        True
        >>> p1 != p2
        True
        >>> p1 != p3
        False
    """

    @protomethod()
    def __eq__(self, other: Self) -> bool:
        ...

    @protomethod()
    def __ne__(self, other: Self) -> bool:
        ...


@impl(Eq.__eq__)
def _impl_eq(cls: type[Eq]):
    fields = fields_of(cls).keys()

    return compile_function(
        "__eq__",
        "def __eq__(self, other):",
        "    if self is other: return True",
        "    if type(self) != type(other): return NotImplemented",
        f"    return ({' and '.join(f'self.{field} == other.{field}' for field in fields)})",
    )


@impl(Eq.__ne__)
def _impl_ne(cls: type[Eq]):
    fields = fields_of(cls).keys()

    return compile_function(
        "__ne__",
        "def __ne__(self, other):",
        "    if self is other: return False",
        "    if type(self) != type(other): return NotImplemented",
        f"    return ({' or '.join(f'self.{field} != other.{field}' for field in fields)})",
    )
