import pytest

from ._pyfig import Pyfig


def test__given_config_without_default__when_instantiating__then_raise_error():
    with pytest.raises(TypeError):
        class _MyConfig(Pyfig):
            no_default_value: int
