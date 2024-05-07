from typing import Iterator
from protobase.core import Trait, fields_of, trait_method


class Repr(Trait):
    """
    Trait that implements the __repr__ function in a class.
    This implementation of __repr__ uses the string representation of all field values of the object.
    Example:
        >>> class Foo(Base, Repr):
        ...     a: int
        ...     b: int
        >>> foo = Foo(a=1, b=2)
        >>> foo
        Foo(a=1, b=2)
    """

    @trait_method
    def __rich_repr__(self) -> Iterator[tuple]: ...

    @trait_method
    def __repr__(self) -> str: ...


@Repr.__repr__.implementer
def _impl_repr(cls: type[Repr]):
    def __repr__(self):
        attrs = filter(_rich_attr_filter, self.__rich_repr__())
        attrs = map(_rich_attr_map, attrs)
        return f"{cls.__qualname__}({', '.join(attrs)})"

    return __repr__


@Repr.__rich_repr__.implementer
def _impl_rich_repr(cls: type[Repr]):
    fields = fields_of(cls)
    defaults = cls.__kwdefaults__

    def __rich_repr__(self):
        for field in fields:
            if field in defaults:
                yield field, getattr(self, field), defaults[field]
            else:
                yield field, getattr(self, field)

    return __rich_repr__


def _rich_attr_filter(attr_info: tuple) -> bool:
    if len(attr_info) == 3 and attr_info[1] == attr_info[2]:
        return False
    return True


def _rich_attr_map(attr_info: tuple) -> str:
    if len(attr_info) == 1:
        return repr(attr_info[0])

    return f"{attr_info[0]}={attr_info[1]!r}"
