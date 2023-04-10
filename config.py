from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseSettings, validator


def yaml_config_settings_source(settings: BaseSettings) -> dict[str, Any]:
    yaml_file = getattr(settings.__config__, "yaml_file", "")

    assert yaml_file, "Settings.yaml_file not properly configured"

    path = Path(yaml_file)

    if not path.exists():
        raise FileNotFoundError(f"Could not open yaml settings file at: {path}")
    return yaml.safe_load(path.read_text("utf-8"))


class OpenAI(BaseSettings):
    base_url: str
    key: str

    @validator("base_url", pre=True, always=True)
    def formatted_base_url(cls, v):
        return f"{v}/v1" if v is not None else v


class Config(BaseSettings):
    openai: OpenAI

    class Config:
        yaml_file = Path("config").resolve().joinpath("config.yaml")
        case_sensitive = True

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                yaml_config_settings_source,
                env_settings,
            )


config = Config()


openai_config = config.openai
