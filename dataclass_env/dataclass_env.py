import os
import dataclasses
from types import NoneType
from typing import Any, Callable, Type, TypeVar

from . import exceptions
from .string_parsers import parse_type

OnSetFn = Callable[[str, Any, bool], None]

T = TypeVar("T")

DataclassType = Type[T]


class MissingValue:
    pass


MISSING_VALUE = MissingValue()


class Env:
    def __init__(
        self,
        name: str,
        default: str | MissingValue,
        file: bool,
        expand: bool,
        prefix: str,
        unset: bool,
        required: bool,
        not_empty: bool,
        separator: str,
    ) -> None:
        self.default = default
        self.name = name
        self.file = file
        self.expand = expand
        self.prefix = prefix
        self.unset = unset
        self.required = required
        self.not_empty = not_empty
        self.separator = separator

        self.type: Type[Any] = NoneType
        self.value: str | None = None
        self.on_set: OnSetFn | None = None

    def __call__(self) -> Any:
        key = f"{self.prefix}{self.name}"

        try:
            is_multi, default_func, do_parse = parse_type(self.type)
        except Exception:
            raise exceptions.UnsupportedTypeError(key, self.type.__name__)

        if self.value is not None:
            value, is_default = self.value, False
        else:
            if (
                self.required
                and key not in os.environ
                and self.default is MISSING_VALUE
            ):
                raise exceptions.RequiredError(key)

            if key in os.environ:
                value, is_default = os.environ[key], False
            else:
                if isinstance(self.default, MissingValue):
                    value = str(default_func())
                else:
                    value = self.default

                is_default = True

        if self.expand:
            value = value.format(**os.environ)

        if self.unset:
            try:
                del os.environ[key]
            except KeyError:
                raise exceptions.UnsetError(key)

        if self.not_empty and value == "":
            raise exceptions.NotEmptyError(key)

        if self.file:
            try:
                with open(value) as fp:
                    value = fp.read()
            except OSError:
                raise exceptions.FileError(key, value)

        try:
            value = do_parse(value.split(self.separator) if is_multi else value)
        except Exception:
            raise exceptions.ParseError(key, value, self.type.__name__)

        if self.on_set is not None:
            self.on_set(key, value, is_default)

        return value


def env(
    name: str,
    *,
    default: str | MissingValue = MISSING_VALUE,
    prefix: str = "",
    required: bool = False,
    unset: bool = False,
    separator: str = ",",
    expand: bool = False,
    not_empty: bool = False,
    file: bool = False,
) -> Any:
    return dataclasses.field(
        default_factory=Env(
            name=name,
            default=default,
            file=file,
            expand=expand,
            prefix=prefix,
            unset=unset,
            required=required,
            not_empty=not_empty,
            separator=separator,
        )
    )


def parse_env(
    dataclass_cls: DataclassType,
    required: bool = False,
    prefix: str = "",
    environment: dict[str, str] | None = None,
    on_set: OnSetFn | None = None,
) -> DataclassType:
    dataclass_cls.__dataclass_env__ = True

    if environment is None:
        environment = {}

    for field in dataclasses.fields(dataclass_cls):
        default_factory = field.default_factory

        if isinstance(default_factory, Env):
            default_factory.type = field.type
            default_factory.on_set = on_set

            if default_factory.name in environment:
                default_factory.value = environment[default_factory.name]

            if prefix:
                default_factory.prefix = f"{prefix}{default_factory.prefix}"

            if required:
                default_factory.required = True

    return dataclass_cls


def dataclass_env(
    dataclass_cls: DataclassType | None = None,
    *,
    required: bool = False,
    prefix: str = "",
    environment: dict[str, str] | None = None,
    on_set: OnSetFn | None = None,
) -> DataclassType | Callable[[DataclassType], DataclassType]:
    if dataclass_cls is None:

        def wrapper(dataclass_cls_: DataclassType) -> DataclassType:
            return parse_env(
                dataclass_cls_,
                required=required,
                prefix=prefix,
                environment=environment,
                on_set=on_set,
            )

        return wrapper

    return parse_env(
        dataclass_cls,
        required=required,
        prefix=prefix,
        environment=environment,
        on_set=on_set,
    )
