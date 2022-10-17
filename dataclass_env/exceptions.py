class DataclassEnvError(Exception):
    pass


class RequiredError(DataclassEnvError):
    def __init__(self, key: str) -> None:
        super().__init__(f"missing required environment variable {key!r}")


class NotEmptyError(DataclassEnvError):
    def __init__(self, key: str) -> None:
        super().__init__(f"environment variable {key!r} is empty")


class UnsetError(DataclassEnvError):
    def __init__(self, key: str) -> None:
        super().__init__(f"environment variable {key!r} is not set")


class FileError(DataclassEnvError):
    def __init__(self, key: str, path: str) -> None:
        super().__init__(f"failed to read file {path!r} for environment variable {key!r}")


class ParseError(DataclassEnvError):
    def __init__(self, key: str, value: str, type_name: str) -> None:
        super().__init__(f"failed to parse {value!r} as {type_name!r} for environment variable {key!r}")


class UnsupportedTypeError(DataclassEnvError):
    def __init__(self, key: str, type_name: str) -> None:
        super().__init__(f"unsupported type {type_name!r} for environment variable {key!r}")
