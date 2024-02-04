from typing import Any
from protobase.core import Trait, Obj, fields_of, impl, protomethod
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
    def __init__(self, **kwargs): ...

    @protomethod()
    def __getstate__(self) -> dict[str, Any]: ...

    def __setstate__(self, state: dict[str, Any]) -> None:
        self.__init__(**state)


@impl(Init.__init__)
def _impl_setstate(cls: type[Obj]):
    fields = fields_of(cls)

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


@impl(Init.__getstate__)
def _impl_getstate(cls: type[Obj]):
    fields = fields_of(cls)

    params = ", ".join(f"{field}=self.{field}" for field in fields)

    return compile_function(
        "__getstate__",
        "def __getstate__(self):",
        f"    return dict({params})",
    )
