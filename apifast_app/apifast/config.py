from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Go up three levels from this file to get to the project root
# apifast_app/apifast/config.py -> apifast_app/apifast -> apifast_app -> project root
env_path = Path(__file__).parent.parent.parent / '.env'

class Config(BaseSettings):
    image_dir: str
    database_uri: str
    redis_uri: str
    gemini_api_key: str
    model_config = SettingsConfigDict(env_file=env_path)

config = Config()
