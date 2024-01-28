from weakref import WeakKeyDictionary, ref

from protobase.core import Trait
from protobase.trait.eq import Eq
from protobase.trait.hash import Hash
from protobase.trait.init import Init
from protobase.trait.inmutable import Inmutable
from protobase.trait.weak import Weak


class Consed(Eq, Hash, Inmutable, Init, Weak, Trait):
    """
    Trait for a class that is a hash-consed object.
    Conses objects are objects that are unique for each set of field values.
    They have a fixed identity and can be compared with 'is'.

    Example:
        >>> class Foo(Base, Consed):
        ...     a: int
        ...     b: int
        ...     c: int
        >>> a = Foo(1, 2, 3)
        >>> b = Foo(1, 2, 3)
        >>> a is b
        True
        >>> c = Foo(1, 2, 4)
        >>> a is c
        False
    """

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.__consing__ = WeakKeyDictionary()

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        if obj in cls.__consing__:
            return cls.__consing__[obj]()
        cls.__consing__[obj] = ref(obj)
        return obj


def consed_count(cls: type[Consed]) -> int:
    """
    Returns the number of instances of `Consed` class.

    Args:
        cls (type[Consed]): The `Consed` class.

    Returns:
        int: The number of instances of `Consed` class.
    Example:
        >>> class Foo(Consed):
        ...     pass
        >>> Foo()
        Foo()
        >>> consed_count(Foo)
        1
        >>> Foo()
        Foo()
        >>> consed_count(Foo)
        1
    """
    return len(cls.__consing__)
