import yaml
from functools import lru_cache

@lru_cache(None)
def load_config(config_path='config.yml'):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config
