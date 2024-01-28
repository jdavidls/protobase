from typing import Iterator
from protobase.core import Trait, fields_of, impl, protomethod
from protobase.utils import compile_function


class Repr(Trait):
    """
    Trait that implements the __repr__ function in a class.
    This implementation of __repr__ uses the string representation of all field values of the object.
    Example:
        >>> class Foo(Base, Repr):
        ...     a: int
        ...     b: int
        >>> foo = Foo(1, 2)
        >>> foo
        Foo(a=1, b=2)
    """

    @protomethod()
    def __repr__(self) -> str:
        ...

    @protomethod()
    def __rich_repr__(self) -> Iterator[tuple]:
        ...

    # for field in type(self):
    #     if field.has_default:
    #         yield field.name, getattr(self, field.name), field.default
    #     else:
    #         yield field.name, getattr(self, field.name)


@impl(Repr.__repr__)
def _repr_impl(cls: type[Repr]):
    fields = fields_of(cls).keys()

    fields_fmt = (f"{field}={{getattr(self, '{field}')}}" for field in fields)
    fstr = f"{cls.__qualname__}({', '.join(fields_fmt)})"

    return compile_function(
        "__repr__",
        f"def __repr__(self):",
        f"    return f{repr(fstr)}",
    )


# if HAS_RICH:
# @Repr.__repr__.impl()
# def _impl_rich_repr(cls: type[Repr]):
#     fields = attrs(cls).keys()

#     return compile_function(
#         "__rich_repr__",
#         f"def __rich_repr__(self):",
#         f'    return f"{type(self).__qualname__}({", ".join(f"{field.name}={{getattr(self, field.name)!r}}" for field in fields)})"',
#     )
