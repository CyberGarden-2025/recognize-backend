from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import logging

import aioboto3
from pydantic import SecretStr

from app.settings import SETTINGS


def safe_s3_call(func):
    def wrapper(self: "AsyncS3Client", *args, **kwargs):
        if self.endpoint_url and self.aws_access_key_id and self.aws_secret_access_key:
            return func(self, *args, **kwargs)

    return wrapper


class AsyncS3Client:
    def __init__(
        self,
        endpoint_url: str,
        aws_access_key_id: SecretStr,
        aws_secret_access_key: SecretStr,
        region_name: str = "us-east-1",
        verify_ssl: bool = False,
    ):
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.verify_ssl = verify_ssl

        self.session = aioboto3.Session()

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator:
        """Асинхронный контекстный менеджер для S3 клиента"""
        async with self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id.get_secret_value(),
            aws_secret_access_key=self.aws_secret_access_key.get_secret_value(),
            region_name=self.region_name,
            verify=self.verify_ssl,
        ) as client:
            yield client

    @safe_s3_call
    async def create_bucket(self, bucket_name: str) -> bool:
        """Создание бакета"""
        try:
            async with self.get_client() as client:
                await client.create_bucket(Bucket=bucket_name)
                logging.info(f"Bucket '{bucket_name}' created successfully")
                return True
        except Exception as e:
            return False

    @safe_s3_call
    async def upload_bytes(
        self, data: bytes, bucket_name: str, object_name: str
    ) -> bool:
        """Загрузка данных из памяти"""
        try:
            async with self.get_client() as client:
                await client.put_object(Bucket=bucket_name, Key=object_name, Body=data)
                logging.info(f"Data uploaded to '{bucket_name}/{object_name}'")
                return True
        except Exception as e:
            logging.exception(f"Error uploading bytes: {e}")
            return False

    async def download_bytes(
        self, bucket_name: str, object_name: str
    ) -> Optional[bytes]:
        """Скачивание данных в память"""
        try:
            async with self.get_client() as client:
                response = await client.get_object(Bucket=bucket_name, Key=object_name)
                async with response["Body"] as stream:
                    data = await stream.read()
                    logging.info(f"Data downloaded from '{bucket_name}/{object_name}'")
                    return data
        except Exception as e:
            logging.exception(f"Error downloading bytes: {e}")
            return None

    async def list_objects(self, bucket_name: str, prefix: str = "") -> list:
        """Список объектов в бакете"""
        try:
            async with self.get_client() as client:
                response = await client.list_objects_v2(
                    Bucket=bucket_name, Prefix=prefix
                )
                return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            logging.exception(f"Error listing objects: {e}")
            return []

    @safe_s3_call
    async def delete_object(self, bucket_name: str, object_name: str) -> bool:
        """Удаление объекта"""
        try:
            async with self.get_client() as client:
                await client.delete_object(Bucket=bucket_name, Key=object_name)
                logging.info(f"Object '{object_name}' deleted from '{bucket_name}'")
                return True
        except Exception as e:
            logging.exception(f"Error deleting object: {e}")
            return False

    async def object_exists(self, bucket_name: str, object_name: str) -> bool:
        """Проверка существования объекта"""
        try:
            async with self.get_client() as client:
                await client.head_object(Bucket=bucket_name, Key=object_name)
                return True
        except Exception as e:
            return False


s3_client = AsyncS3Client(
    endpoint_url=SETTINGS.S3_ENDPOINT,
    aws_access_key_id=SETTINGS.S3_ACCESS_KEY,
    aws_secret_access_key=SETTINGS.S3_SECRET_KEY,
)
