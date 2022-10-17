# dataclass-env

`dataclass-env` is a library for loading environment variables into `dataclasses`. Inspired by https://github.com/caarlos0/env.

## Example

```shell
export PASSWORD=123456
export HOSTS=localhost:127.0.0.1
export PRODUCTION=True
```

```python
from dataclasses import dataclass
from dataclass_env import dataclass_env, env


@dataclass_env
@dataclass
class Config:
    home: str = env("HOME")
    port: int = env("PORT", default="3000")
    password: str = env("PASSWORD", unset=True)
    is_production: bool = env("PRODUCTION")
    hosts: list[str] = env("HOSTS", separator=":")
    temp_folder: str = env("TEMP_FOLDER", default="{HOME}/tmp", expand=True)


def main() -> None:
    config = Config()

    print(config)


if __name__ == "__main__":
    main()
```

```text
Config(home='/Users/meir', port=3000, password='123456', is_production=True, hosts=['localhost', '127.0.0.1'], temp_folder='/Users/meir/tmp')
```
