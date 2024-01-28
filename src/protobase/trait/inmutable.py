from typing import NoReturn
from protobase.core import Trait
from protobase.trait.init import Init


class Inmutable(Init, Trait):
    """
    Trait for making a class readonly.
    This trait overrides the __setattr__ method to raise an AttributeError.
    Example:
        >>> class Foo(Base, Inmutable):
        ...     a: int
        ...     b: int
        >>> foo = Foo(1, 2)
        >>> foo.a
        1
        >>> foo.a = 2
        Traceback (most recent call last):
            ...
        AttributeError: Cannot set attribute a. Foo is readonly.
    """

    def __setattr__(self, nm, val) -> NoReturn:
        raise AttributeError(
            f"Cannot set attribute '{nm}'. {type(self).__qualname__} is readonly."
        )
