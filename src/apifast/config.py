from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    image_dir: str
    database_uri: str
    model_config = SettingsConfigDict(env_file='.env')

config = Config()
