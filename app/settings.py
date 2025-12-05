from os import environ
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr

load_dotenv(".env")


class Settings(BaseModel):
    IS_DEBUG: bool
    LOGGING_LEVEL: str
    API_HOST: str
    API_PORT: int

    HTTP_PROXY_SERVER: Optional[SecretStr] = None

    OPENAI_API_BASE: str
    OPENAI_API_KEY: SecretStr
    OPENAI_GPT_MODEL: str

    S3_ENDPOINT: Optional[str]
    S3_ACCESS_KEY: Optional[SecretStr] = None
    S3_SECRET_KEY: Optional[SecretStr] = None
    S3_BUCKET_NAME: Optional[str]


SETTINGS = Settings(**environ)
