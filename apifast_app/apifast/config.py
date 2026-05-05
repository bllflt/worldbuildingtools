from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    image_dir: str
    database_uri: str
    redis_uri: str
    llm_proxy_url: str
    jwt_secret: str
    jwt_token_ttl: int
    model_config = SettingsConfigDict(env_file=find_dotenv())


config = Config()
