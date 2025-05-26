import pprint
from typing import TypeVar


def address_string(addr: tuple[str, int]) -> str:
    return f"{addr[0]}:{addr[1]}"


def object_str(obj: object) -> str:
    return pprint.pformat(obj, indent=2, compact=False)


_T = TypeVar("_T")


def get_or(val: _T | None, default: _T) -> _T:
    return default if val is None else val
