import pytest

from dataclass_env.string_parsers import str_to_bool


def test_str_to_bool():
    assert str_to_bool("true") is True
    assert str_to_bool("false") is False

    assert str_to_bool("YES") is True

    with pytest.raises(ValueError):
        assert str_to_bool("OK")
