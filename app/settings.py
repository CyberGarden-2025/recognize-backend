from os import environ
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr

load_dotenv(".env")


class Settings(BaseModel):
    IS_DEBUG: bool = False
    LOGGING_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    HTTP_PROXY_SERVER: Optional[SecretStr] = None

    OPENAI_API_BASE: str
    OPENAI_API_KEY: SecretStr
    OPENAI_GPT_MODEL: str

    S3_ENDPOINT: Optional[str] = None
    S3_ACCESS_KEY: Optional[SecretStr] = None
    S3_SECRET_KEY: Optional[SecretStr] = None
    S3_BUCKET_NAME: Optional[str] = None


SETTINGS = Settings(**environ)
