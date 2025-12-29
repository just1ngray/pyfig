from typing import List, Dict, Tuple
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field

from ._pyfig import Pyfig
from ._debug import PyfigDebug


def test__given_simple_model__when_pyfig_debug_wrap__then_tracks_access():
    class SimpleConfig(Pyfig):
        foo: str = "foo"
        bar: str = "bar"

    original = SimpleConfig()
    tracking = PyfigDebug.wrap(original)
    assert isinstance(tracking, SimpleConfig)

    print(original.foo)
    print(tracking.bar)

    assert isinstance(tracking, PyfigDebug)
    assert tracking.pyfig_debug_field_accesses("foo") == 0
    assert tracking.pyfig_debug_field_accesses("bar") == 1
    print(tracking.bar)
    assert tracking.pyfig_debug_field_accesses("bar") == 2
    assert list(tracking.pyfig_debug_unused()) == ["foo"]

def test__given_nested_model__when_pyfig_debug_wrap__then_tracks_access():
    class LoggingConfig(Pyfig):
        level: str = "INFO"
        stdout: bool = False
        stderr: bool = True

    class DeadModuleConfig(Pyfig):
        unused: bool = True

    class SomeServiceConfig(Pyfig):
        enabled: bool = True
        interval_seconds: float = 3.14

    class AnotherServiceConfig(Pyfig):
        enabled: bool = False
        path: Path = Path("path.txt")

    class ServicesConfig(Pyfig):
        some_service: SomeServiceConfig = SomeServiceConfig()
        another_service: AnotherServiceConfig = AnotherServiceConfig()

    class RootConfig(Pyfig):
        logging: LoggingConfig = LoggingConfig()
        services: ServicesConfig = ServicesConfig()
        dead: DeadModuleConfig = DeadModuleConfig()

    def main(cfg: RootConfig):
        print(f"Setting up {cfg.logging.level} level logging...")
        if cfg.services.some_service.enabled:
            print(f"Running SomeService every {cfg.services.some_service.interval_seconds} seconds...")
        if cfg.services.another_service.enabled:
            print(f"Running AnotherService against {cfg.services.another_service.path.as_posix()}")

    root = RootConfig()
    # it does not matter if the other configs are used elsewhere
    main(root)

    tracked = PyfigDebug.wrap(root)
    main(tracked)

    # it does not matter if the other configs are used elsewhere
    main(root)

    if isinstance(tracked, PyfigDebug):
        assert set(tracked.pyfig_debug_unused()) == {
            "dead",
            "logging.stdout",
            "logging.stderr",
            "services.another_service.path",
        }
        assert dict(tracked.pyfig_debug_accesses()) == {
            "logging": 1,
            "logging.level": 1,
            "logging.stdout": 0,
            "logging.stderr": 0,
            "services": 3,
            "services.some_service": 2,
            "services.some_service.enabled": 1,
            "services.some_service.interval_seconds": 1,
            "services.another_service": 1,
            "services.another_service.enabled": 1,
            "services.another_service.path": 0,
            "dead": 0,
            "dead.unused": 0,
        }
    else:
        raise RuntimeError("It must be an instance. The isinstance check just demonstrates how to "
                           "incorporate this nicely into your 'main' with good typing")

def test__given_list_of_configs__when_pyfig_debug_wrap__then_tracks_elements_too():
    class Thing(BaseModel):
        name: str
        id: str = Field(default_factory=lambda: str(uuid4()))

    class Config(Pyfig):
        things: List[Thing] = [
            Thing(name="foo"),
            Thing(name="bar"),
            Thing(name="baz"),
        ]

    cfg = Config()
    dbg = PyfigDebug.wrap(cfg)

    print(dbg.things[0].name, dbg.things[0].id)
    print(dbg.things[1].name)

    assert isinstance(dbg, PyfigDebug)
    assert dict(dbg.pyfig_debug_accesses()) == {
        "things": 3,
        "things[0].name": 1,
        "things[0].id": 1,
        "things[1].name": 1,
        "things[1].id": 0,
        "things[2].name": 0,
        "things[2].id": 0,
    }

def test__given_2d_list__when_pyfig_debug_wrap__then_tracks_recursively():
    class Thing(BaseModel):
        id: str = Field(default_factory=lambda: str(uuid4()))

    class Config(Pyfig):
        things: List[List[Thing]] = [
            [Thing(), Thing(), Thing()],
            [Thing(), Thing()],
        ]

    cfg = Config()
    dbg = PyfigDebug.wrap(cfg)

    print(dbg.things[0][2].id)
    print(dbg.things[1][0].id)

    assert isinstance(dbg, PyfigDebug)
    assert dict(dbg.pyfig_debug_accesses()) == {
        "things": 2,
        "things[0][0].id": 0,
        "things[0][1].id": 0,
        "things[0][2].id": 1,
        "things[1][0].id": 1,
        "things[1][1].id": 0,
    }

def test__given_dict_config__when_pyfig_debug_wrap__then_tracks_values():
    class Id(BaseModel):
        id: str = Field(default_factory=lambda: str(uuid4()))

    class Config(Pyfig):
        mapping: Dict[str, Id] = {
            "foo": Id(),
            "bar": Id(),
        }

    cfg = Config()
    dbg = PyfigDebug.wrap(cfg)

    print(dbg.mapping["foo"].id)

    assert isinstance(dbg, PyfigDebug)
    assert dict(dbg.pyfig_debug_accesses()) == {
        "mapping": 1,
        "mapping['foo'].id": 1,
        "mapping['bar'].id": 0,
    }

def test__given_dict_config__when_pyfig_debug_wrap__then_tracks_values_recursively():
    class Id(BaseModel):
        id: str = Field(default_factory=lambda: str(uuid4()))

    class Config(Pyfig):
        mapping2d: Dict[Tuple[str, str], Dict[str, Id]] = {
            ("a", "b"): {
                "foo": Id(),
                "bar": Id(),
            },
            ("c", "d"): {
                "baz": Id(),
            },
        }

    cfg = Config()
    dbg = PyfigDebug.wrap(cfg)

    print(dbg.mapping2d[("a", "b")]["foo"].id)
    print(dbg.mapping2d[("c", "d")]["baz"].id)

    assert isinstance(dbg, PyfigDebug)
    assert dict(dbg.pyfig_debug_accesses()) == {
        "mapping2d": 2,
        "mapping2d[('a', 'b')]['foo'].id": 1,
        "mapping2d[('a', 'b')]['bar'].id": 0,
        "mapping2d[('c', 'd')]['baz'].id": 1,
    }
