from weakref import WeakKeyDictionary, ref

from protobase.core import Object, Trait

from .cmp import Eq
from .hash import Hash
from .init import Init
from .inmutable import Inmutable
from .weak import Weak


class Consed(Hash, Eq, Inmutable, Init, Weak, Trait):
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

    __slots__ = ("__hash_cache__",)

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if issubclass(cls, Object):
            cls.__consing__ = WeakKeyDictionary()

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        try:
            if self in cls.__consing__:
                return cls.__consing__[self]()
        except TypeError as exc:
            raise ValueError(f"Cannot hash-consed mutable object: {self}") from exc

        cls.__consing__[self] = ref(self)
        return self


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
