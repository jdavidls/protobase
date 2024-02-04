from types import NotImplementedType
from typing import Literal, Self, Sequence
from protobase.core import Trait, fields_of, impl, protomethod
from protobase.utils import compile_function


class Eq(Trait):
    """
    A trait that enables equality operators (__eq__, __ne__) based on
    the fields of a proto object.

    Example:

        >>> from protobase.core import Obj
        >>> from protobase.trait import Eq
        >>>
        >>> class Point(Obj, Eq):
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
    def __eq__(self, other: Self) -> bool: ...

    @protomethod()
    def __ne__(self, other: Self) -> bool: ...


@impl(Eq.__eq__)
def _impl_eq(cls: type[Eq]):
    fields = fields_of(cls)

    return compile_function(
        "__eq__",
        "def __eq__(self, other):",
        "    if self is other: return True",
        "    if type(self) != type(other): return NotImplemented",
        f"    return ({' and '.join(f'self.{field} == other.{field}' for field in fields)})",
    )


@impl(Eq.__ne__)
def _impl_ne(cls: type[Eq]):
    fields = fields_of(cls)

    return compile_function(
        "__ne__",
        "def __ne__(self, other):",
        "    if self is other: return False",
        "    if type(self) != type(other): return NotImplemented",
        f"    return ({' or '.join(f'self.{field} != other.{field}' for field in fields)})",
    )


class Cmp(Eq):
    @protomethod()
    def __lt__(self, other: Self) -> NotImplementedType | bool: ...

    @protomethod()
    def __gt__(self, other: Self) -> NotImplementedType | bool: ...

    def __le__(self, other: Self) -> NotImplementedType | bool:
        res = self.__gt__(other)
        return NotImplemented if res is NotImplemented else not res

    def __ge__(self, other: Self) -> NotImplementedType | bool:
        res = self.__lt__(other)
        return NotImplemented if res is NotImplemented else not res


def _compile_cmp_function(
    ct_name: Literal["__lt__", "__gt__"],
    ce_name: Literal["__ge__", "__le__"],
    fields: Sequence[str],
):
    fields = list(fields)
    return compile_function(
        ct_name,
        f"def {ct_name}(self, other):",
        "    if type(self) != type(other): return NotImplemented",
        # "    if self is other: return False",
        *[
            f"    if (res := self.{field}.{ct_name}(other.{field})) or self.{field}.__ne__(other.{field}): return res"
            for field in fields[:-1]
        ],
        f"    return self.{fields[-1]}.{ct_name}(other.{fields[-1]})",
    )


@impl(Cmp.__lt__)
def _impl_lt(cls: type[Cmp]):
    return _compile_cmp_function("__lt__", "__ge__", fields_of(cls))


@impl(Cmp.__gt__)
def _impl_gt(cls: type[Cmp]):
    return _compile_cmp_function("__gt__", "__le__", fields_of(cls))
