from protobase.core import Trait, Base, fields_of, impl, protomethod
from protobase.utils import compile_function, attr_lookup


class Init(Trait):
    """
    Trait for initializing fields on a class.
    This trait automatically generates an __init__ method for the class, with
    keyword-only arguments for each field.

    Example:
        >>> class Foo(Base, Init):
        ...     x: int = 1
        ...     y: int = 2
        >>> foo = Foo(x=3)
        >>> foo.x
        3
        >>> foo.y
        2
    """

    @protomethod()
    def __init__(self, **kwargs):
        ...


@impl(Init.__init__)
def _init_impl(cls: type[Base]):
    fields = fields_of(cls).keys()

    return compile_function(
        "__init__",
        f'def __init__(self, *, {", ".join(fields)}):',
        *[f"    global {field}_setter" for field in fields],
        *[f"    {field}_setter(self, {field})" for field in fields],
        globals={
            f"{field}_setter": attr_lookup(cls, field).__set__ for field in fields
        },
        __kwdefaults__=cls.__kwdefaults__,
        # __defaults__=cls.__defaults__,
    )
