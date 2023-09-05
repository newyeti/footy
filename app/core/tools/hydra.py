from omegaconf import OmegaConf
from hydra import compose, initialize_config_dir
from pydantic import ValidationError
from app.entrypoints.cmd.config import CliAppConfig

def load_app_config(config_dir: str, config_name: str, version_base = "1.3"):
    # Initialize the config directory for Hydra
    initialize_config_dir(config_dir=config_dir, version_base=version_base)

    # Load the configuration using Hydra
    config = compose(config_name=config_name)

    # Convert the OmegaConf config to a Pydantic model
    try:
        app_config = CliAppConfig(**OmegaConf.to_container(config.app, resolve=True))
    except ValidationError as e:
        print(f"Invalid configuration: {e}")
        return None

    return app_config