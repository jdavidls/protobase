from protobase.core import Trait


class DynamicAttrs(Trait):
    """
    Trait for enabling dynamic attributes on a class.

    Example:
        >>> class Foo(Base, DynamicAttrs):
        ...     pass
        >>> foo = Foo()
        >>> foo.bar = 1
        >>> foo.bar
        1
    """

    __slots__ = ("__dict__",)
    # __dict__: dict[str, Any]
