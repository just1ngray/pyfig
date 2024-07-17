from .config import ApplicationConfig, get_config


def test__given_example_setup__when_metaconf_config__then_config_is_loaded():
    cfg = get_config()

    assert cfg == ApplicationConfig(**{
        "name": "Production Application",
        "version": "0.1.0",
        "log_level": "INFO",
        "modules": {
            "health_monitor": {
                "enabled": True,
                "interval_seconds": 30
            },
            "important_task": {
                "enabled": True,
                "resource": "https://production.example.com/important_task",
                "api_key": "mocked api key",
                "params": {
                    "timeout": 60,
                    "retries": 100
                }
            }
        }
    })
