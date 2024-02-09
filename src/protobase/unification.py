from typing import Any
from protobase.core import Obj, Trait


class UnificationVar(Trait): ...


# talvez deba ser un generador de multiples unificadores?
## multiples soluciones


def unify(*objs: tuple[Obj, ...]) -> dict[UnificationVar, Any]: ...
