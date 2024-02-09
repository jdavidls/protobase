from typing import Any, Iterator, TypeVar, overload

from protobase.core import Obj, fields_of


T = TypeVar("T", bound=Obj)


def names_of(cls: type[Obj]) -> Iterator[str]:
    return fields_of(cls)


@overload
def zip(
    self: T, *others: tuple[T], with_names: False
) -> Iterator[tuple[Any, *tuple[Any, ...]]]: ...


@overload
def zip(
    self: T, *others: tuple[T], with_names: True
) -> Iterator[tuple[str, tuple[Any, *tuple[Any, ...]]]]: ...


def zip(
    self: T, *others: tuple[T], with_names: bool = False
) -> Iterator[tuple[Any, *tuple[Any, ...]]]:
    cls = type(self)

    if not all(isinstance(other, cls) for other in others):
        invalid_classes = filter(lambda other: not isinstance(other, cls), others)
        raise TypeError(f"Cannot zip {cls} with {invalid_classes}")

    if with_names:
        for field in fields_of(cls):
            yield field, (
                getattr(self, field),
                *(getattr(other, field) for other in others),
            )
    else:

        for field in fields_of(cls):
            yield getattr(self, field), *(getattr(other, field) for other in others)


def lookup(cls: type, nm: str):
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
