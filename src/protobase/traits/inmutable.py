from decimal import Decimal
from types import GenericAlias
from typing import NoReturn, get_args, get_origin

from protobase.utils import can_import

from ..core import Trait, fields_of
from .init import Init

KNOW_INMUTABLE_TYPES: set[type] = {
    type(None),
    type(...),
    type(fields_of),  # function type is accepted as inmutable
    bool,
    int,
    float,
    bytes,
    str,
    tuple,
    frozenset,
    Decimal,
}

if can_import("frozendict"):
    from frozendict import frozendict

    KNOW_INMUTABLE_TYPES.add(frozendict)


def is_inmutable(cls: type) -> bool:
    """
    Check if a class is immutable.

    Args:
        cls (type): The class to check.

    Returns:
        bool: True if the class is immutable, False otherwise.

    Example:
        >>> is_inmutable(int)
        True
        >>> is_inmutable(str)
        True
        >>> is_inmutable(list)
        False
        >>> is_inmutable(dict)
        False
    """
    for base in cls.__mro__:
        if base in KNOW_INMUTABLE_TYPES:
            return True
    return False


def know_inmutable(tp: type):
    """
    Adds the given type to the set of known immutable types. This can be used
    as a decorator.

    Args:
        type (type): The type to be added.

    Returns:
        type: The added type.

    Example:
        >>> @know_inmutable
        ... class Foo:
        ...     pass
        >>> is_inmutable(Foo)
    """

    KNOW_INMUTABLE_TYPES.add(tp)
    return tp


@know_inmutable
class Inmutable(Init, Trait):
    """Trait for making a class readonly.

    This trait overrides the __setattr__ method to raise an AttributeError.

    A Inmutable class can be used as a key in a dict or as an element in a set.

    Hashing is cached for Inmutable classes. This means that if the hash of an
    Inmutable object is calculated, it will be stored in the __hash_cache__ slot
    of the object. This is done to avoid recalculating the hash of the object
    every time it is hashed.1

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

    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
        # cls.__dict__["__setattr__"] = Inmutable.__setattr__

    @classmethod
    def __check_type_hints__(cls):
        super().__check_type_hints__()

        def check_inmutable(nm: str, tp: GenericAlias | type):
            if isinstance(tp, GenericAlias):
                orig = get_origin(tp)

                if not is_inmutable(orig):
                    raise TypeError(
                        f"Attribute {nm} of generic argument '{tp}' is not a know inmutable."
                    )

                for arg in get_args(tp):
                    check_inmutable(nm, arg)

            elif isinstance(tp, type):
                if not is_inmutable(tp):
                    raise TypeError(
                        f"Attribute '{nm}' of type '{tp}' is not a know inmutable."
                    )

        for nm, tp in fields_of(cls).items():
            check_inmutable(nm, tp)

    __slots__ = ("__hash_cache__",)

    @classmethod
    def __class_call__(cls, *args, **kwargs):
        return cls.__new__(cls, *args, **kwargs)

    def __new__(cls, *args, **kwargs):
        self = super(Inmutable, cls).__new__(cls, *args, **kwargs)
        super(Inmutable, self).__init__(*args, **kwargs)
        return self

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Init cannot be called on Inmutable classes")

    def __getnewargs_ex__(self) -> tuple[tuple, dict]:
        return (), {nm: getattr(self, nm) for nm in fields_of(type(self))}

    def __getstate__(self) -> None:
        pass

    def __setstate__(self, state) -> None:
        pass

    def __setattr__(self, nm, val) -> NoReturn:
        raise AttributeError(
            f"Cannot set attribute '{nm}'. {type(self).__qualname__} is inmutable."
        )
