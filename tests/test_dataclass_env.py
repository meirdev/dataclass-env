import os
import tempfile
from dataclasses import dataclass
from typing import Iterable, Generic, TypeVar

import pytest

from dataclass_env import dataclass_env, env
from dataclass_env import exceptions


def test_field():
    os.environ["HOME"] = "/home/user"

    @dataclass_env
    @dataclass
    class Config:
        home: str = env("HOME")

    config = Config()

    assert config.home == "/home/user"


def test_field_types():
    os.environ["HOME"] = "/home/user"
    os.environ["PORT"] = "3000"
    os.environ["PRODUCTION"] = "true"
    os.environ["HOSTS"] = "localhost:127.0.0.1"

    @dataclass_env
    @dataclass
    class Config:
        home: str = env("HOME")
        port: int = env("PORT", default="3000")
        is_production: bool = env("PRODUCTION")
        hosts: list[str] = env("HOSTS", separator=":")

    config = Config()

    assert config.home == "/home/user"
    assert config.port == 3000
    assert config.is_production is True
    assert config.hosts == ["localhost", "127.0.0.1"]


def test_field_unsupported_type():
    class Port:
        def __init__(self, port: str):
            pass

    T = TypeVar("T")

    class HostList(Generic[T]):
        def __init__(self, hosts: Iterable[str]):
            pass

    @dataclass_env
    @dataclass
    class Config:
        port: Port = env("PORT")

    with pytest.raises(exceptions.UnsupportedTypeError):
        Config()

    @dataclass_env
    @dataclass
    class Config:
        hosts: HostList[str] = env("HOSTS", separator=":")

    with pytest.raises(exceptions.UnsupportedTypeError):
        Config()


def test_field_type_convert_error():
    os.environ["PORT"] = "3000a"

    @dataclass_env
    @dataclass
    class Config:
        port: int = env("PORT")

    with pytest.raises(exceptions.ParseError):
        Config()


def test_field_default():
    if "PORT" in os.environ:
        del os.environ["PORT"]

    @dataclass_env
    @dataclass
    class Config:
        port: int = env("PORT", default="3000")

    config = Config()

    assert config.port == 3000


def test_field_prefix():
    os.environ["APP_PORT"] = "3000"

    @dataclass_env
    @dataclass
    class Config:
        port: int = env("PORT", prefix="APP_")

    config = Config()

    assert config.port == 3000


def test_field_expand():
    os.environ["HOME"] = "/home/user"
    os.environ["TEMP_FOLDER"] = "{HOME}/tmp"

    @dataclass_env
    @dataclass
    class Config:
        temp_folder: str = env("TEMP_FOLDER", default="{HOME}/tmp", expand=True)

    config = Config()

    assert config.temp_folder == "/home/user/tmp"


def test_field_required():
    if "PORT" in os.environ:
        del os.environ["PORT"]

    @dataclass_env
    @dataclass
    class Config:
        port: int = env("PORT", required=True)

    with pytest.raises(exceptions.RequiredError):
        Config()


def test_field_unset():
    os.environ["PASSWORD"] = "123456"

    @dataclass_env
    @dataclass
    class Config:
        password: str = env("PASSWORD", unset=True)

    config = Config()

    assert "PASSWORD" not in os.environ
    assert config.password == "123456"


def test_field_unset_key_error():
    if "PORT" in os.environ:
        del os.environ["PORT"]

    @dataclass_env
    @dataclass
    class Config:
        port: int = env("PORT", unset=True)

    with pytest.raises(exceptions.UnsetError):
        Config()


def test_field_not_empty():
    os.environ["PASSWORD"] = ""

    @dataclass_env
    @dataclass
    class Config:
        password: str = env("PASSWORD", not_empty=True)

    with pytest.raises(exceptions.NotEmptyError):
        Config()


def test_field_file():
    with tempfile.NamedTemporaryFile() as f:
        f.write(b"123456")
        f.flush()

        os.environ["PASSWORD"] = f.name

        @dataclass_env
        @dataclass
        class Config:
            password: str = env("PASSWORD", file=True)

        config = Config()

        assert config.password == "123456"


def test_field_file_not_found():
    os.environ["PASSWORD"] = "not_found"

    @dataclass_env
    @dataclass
    class Config:
        password: str = env("PASSWORD", file=True)

    with pytest.raises(exceptions.FileError):
        Config()


def test_class_prefix():
    os.environ["APP_HOME"] = "/home/user"
    os.environ["APP_PORT"] = "3000"

    @dataclass_env(prefix="APP_")
    @dataclass
    class Config:
        home: str = env("HOME")
        port: int = env("PORT")

    config = Config()

    assert config.home == "/home/user"
    assert config.port == 3000


def test_class_required():
    if "PORT" in os.environ:
        del os.environ["PORT"]

    @dataclass_env(required=True)
    @dataclass
    class Config:
        port: int = env("PORT")

    with pytest.raises(exceptions.RequiredError):
        Config()


def test_class_on_set():
    calls = []

    def on_set(*args):
        calls.append(args)

    os.environ["PORT"] = "3000"

    if "PRODUCTION" in os.environ:
        del os.environ["PRODUCTION"]

    @dataclass_env(on_set=on_set)
    @dataclass
    class Config:
        port: int = env("PORT")
        production: bool = env("PRODUCTION", default="t")

    Config()

    assert ("PRODUCTION", True, True) in calls
    assert ("PORT", 3000, False) in calls


def test_class_environment():
    os.environ["PORT"] = "2000"

    @dataclass_env(environment={"PORT": "3000"})
    @dataclass
    class Config:
        port: int = env("PORT")

    config = Config()

    assert config.port == 3000
