import typing
from typing import Any, Callable, Sequence, Type

StringParserFn = Callable[[Any], Any]


def str_to_bool(string: str) -> bool:
    true = ["y", "yes", "t", "true", "on", "1"]
    false = ["n", "no", "f", "false", "off", "0"]

    value = string.lower()

    if value in true:
        return True
    elif value in false:
        return False

    raise ValueError(f"invalid truth value {value!r}")


def parse_type(type_: Type[Any]) -> tuple[bool, Type[Any], StringParserFn]:
    origin = typing.get_origin(type_)
    args = typing.get_args(type_)

    get = string_parsers

    if origin is None:
        return False, type_, get[type_]

    if len(args) == 1 and isinstance(origin(), Sequence):
        return True, origin, lambda v: origin(get[args[0]](i) for i in v)  # type: ignore[misc]

    raise ValueError(f"unsupported type {type_!r}")


string_parsers: dict[Type[Any], StringParserFn] = {
    int: int,
    float: float,
    str: str,
    bool: str_to_bool,
}
