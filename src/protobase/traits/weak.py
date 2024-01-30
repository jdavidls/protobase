from protobase.core import Trait


class Weak(Trait):
    """
    Trait for enabling weak references on a class.
    This trait adds the __weakref__ slot to the class.

    Example:
        >>> class Foo(Base, Weak):
        ...     a: int
        ...     b: int
        >>> foo = Foo(1, 2)
        >>> weak = ref(foo)
        >>> weakref_count(weak)
        1
    """

    __slots__ = ("__weakref__",)


def weakref_count(weak: Weak) -> int:
    """
    Returns the number of weak references to the object.
    """
    return len(weak.__weakref__)
