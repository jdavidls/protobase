from threading import RLock
from typing import Any, Iterator, TypeVar, overload

from protobase.core import Object, fields_of


T = TypeVar("T", bound=Object)


def names_of(cls: type[Object]) -> Iterator[str]:
    return fields_of(cls)


@overload
def zip(  # pylint: disable=W0662
    self: T, *others: tuple[T], with_names: False
) -> Iterator[tuple[Any, *tuple[Any, ...]]]: ...


@overload
def zip(
    self: T, *others: tuple[T], with_names: True
) -> Iterator[tuple[str, tuple[Any, *tuple[Any, ...]]]]: ...


def zip(
    self: T, *others: tuple[T], with_names: bool = False
) -> Iterator[tuple[Any, *tuple[Any, ...]]]:
    """Zip attributes from multiple Obj instances together.

    This zips the attributes of this Obj instance together with
    the attributes of other Obj instances. If `with_names` is
    True, the attribute names are included. Otherwise, just
    the attribute values are zipped together.

    Checks that all instances are of the same class before
    zipping. Raises TypeError if any instances are not the
    same class.
    """

    cls = type(self)

    if not all(isinstance(other, cls) for other in others):
        invalid_classes = filter(lambda other: not isinstance(other, cls), others)
        raise TypeError(f"Cannot zip {cls} with {invalid_classes}")

    if with_names:
        for field in fields_of(cls):
            yield (
                field,
                (
                    getattr(self, field),
                    *(getattr(other, field) for other in others),
                ),
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


def setter(cls: type, field: str):
    return lookup(cls, field).__set__


def set(obj: Any, field: str, value: Any):
    setter(type(obj), field)(obj, value)


_NOT_FOUND = object()


class slot_cached:
    def __init__(self, func):
        self.slotname = None
        self.lock = RLock()
        self.func = func
        self.__doc__ = func.__doc__
        self.setter = None

    def __set_name__(self, owner, name):
        if self.slotname is None:
            self.slotname = f"_{name}"
        elif name != self.slotname:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                f"({self.slotname!r} and {name!r})."
            )

        if self.slotname not in owner.__slots__:
            raise TypeError(
                f"Cannot assign cached_property to class without slot {self.slotname!r}."
                f" Add {self.slotname!r} to __slots__ in {owner.__qualname__}."
            )

        self.setter = setter(owner, self.slotname)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.slotname is None:
            raise TypeError(
                "Cannot use cached_property instance without slotname initialization."
            )

        val = getattr(instance, self.slotname, _NOT_FOUND)

        if val is _NOT_FOUND:
            with self.lock:
                # check if another thread filled cache while we awaited lock
                val = getattr(instance, self.slotname, _NOT_FOUND)
                if val is _NOT_FOUND:
                    val = self.func(instance)
                    self.setter(instance, val)

        return val
