from typing import Any
from protobase import attr
from protobase.core import Trait, Object, fields_of, trait_method
from protobase.utils import compile_function


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

    @trait_method
    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    @trait_method
    def __getstate__(self) -> dict[str, Any]: ...

    def __setstate__(self, state: dict[str, Any]) -> None:
        self.__init__(**state)


@Init.__init__.implementer
def _impl_init(cls: type[Object]):
    fields = fields_of(cls)

    if len(fields) == 0:
        return compile_function(
            "def __init__(self):",
            "    pass",
        )

    return compile_function(
        f"def __init__(self, *, {", ".join(fields)}):",
        *[f"    global {field}_setter" for field in fields],
        *[f"    {field}_setter(self, {field})" for field in fields],
        globals={f"{field}_setter": attr.setter(cls, field) for field in fields},
        __kwdefaults__=cls.__kwdefaults__,
        # __defaults__=cls.__defaults__,
    )


@Init.__getstate__.implementer
def _impl_getstate(cls: type[Object]):
    fields = fields_of(cls)

    params = ", ".join(f"{field}=self.{field}" for field in fields)

    return compile_function(
        "def __getstate__(self):",
        f"    return dict({params})",
    )
