from itertools import chain
from typing import Any, Callable, Sequence


def _mro(cls):
    if cls is object:
        return [object]
    return [cls] + _mro_merge([_mro(base) for base in cls.__bases__])


def _mro_merge(mros):
    if not any(mros):  # all lists are empty
        return []  # base case
    for candidate, *_ in mros:
        if all(candidate not in tail for _, *tail in mros):
            return [candidate] + _mro_merge(
                [tail if head is candidate else [head, *tail] for head, *tail in mros]
            )
    else:
        raise TypeError("No legal mro")


def mro_of_bases(bases: Sequence[type]):
    return _mro_merge([_mro(base) for base in bases])


def attr_lookup(cls: type, nm: str):
    """
    Look up a attribute by name in the class hierarchy without
    triggering the __getattribute__ mechanism.

    Args:
        cls (type): The class to search in.
        nm (str): The name of the descriptor to look up.

    Returns:
        object: The descriptor object.

    Raises:
        AttributeError: If the descriptor cannot be found in the class hierarchy.

    """
    for base in cls.__mro__:
        if nm in base.__dict__:
            return base.__dict__[nm]
    raise AttributeError(f"Cannot find '{nm}' in '{cls.__qualname__}'")


def compile_function(
    name: str,
    *source,
    locals: dict[str, Any] | None = None,
    globals: dict[str, Any] | None = None,
    **kwargs,
) -> Callable:
    """
    Compile a function from source code.

    Args:
        name (str): The name of the function.
        *source: The source code of the function.
        locals (dict[str, Any] | None, optional): Local variables to be used during execution. Defaults to None.
        globals (dict[str, Any] | None, optional): Global variables to be used during execution. Defaults to None.
        **kwargs: Additional keyword arguments to be set as attributes of the compiled function.

    Returns:
        Callable: The compiled function.
    Example:
        >>> fn = compile_function(
        ...     "foo",
        ...     "def foo(x: int, y: int) -> int:",
        ...     "    return x + y",
        ... )
        >>> fn(1, 2)
        3
        >>> fn.__source__
        'def foo(x: int, y: int) -> int:\n    return x + y\n    \n    \n'
    """
    if locals is None:
        locals = {}

    source = "\n".join(source)
    exec(source, globals, locals)
    fn = locals[name]
    fn.__source__ = source
    for nm, val in kwargs.items():
        setattr(fn, nm, val)
    return fn


def slots_of(cls: type):
    """
    Returns a tuple of all the slots defined in the class and its base classes.

    Args:
        cls (type): The class to retrieve slots from.

    Returns:
        tuple: A tuple containing all the slots defined in the class and its base classes.

    Example:
        >>> class Base:
        ...     __slots__ = ("a", "b")
        >>> class Sub(Base):
        ...     __slots__ = ("c", "d")
        >>> slots_of(Sub)
        ('c', 'd', 'a', 'b')
    """
    return tuple(
        chain.from_iterable(
            base.__slots__
            for base in reversed(cls.__mro__)
            if hasattr(base, "__slots__")
        )
    )


def can_import(module: str) -> bool:
    try:
        __import__(module)
        return True
    except ImportError:
        return False
