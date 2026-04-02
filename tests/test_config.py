from app.config.settings import load_yaml_config


def test_load_yaml_config() -> None:
    cfg = load_yaml_config("config/settings.yaml")
    assert cfg.research["in_sample_ratio"] == 0.7
