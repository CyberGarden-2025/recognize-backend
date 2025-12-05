import io
import asyncio
from typing import Optional

from httpx import AsyncClient
from httpx._types import ProxyTypes
from openai import AsyncOpenAI

from .classify_garbage import GarbageCategory
from app.settings import SETTINGS


class AdvicePicker:
    def __init__(
        self,
        openai_base_url: str,
        openai_api_key: str,
        proxy: Optional[ProxyTypes] = None,
    ):
        self.openai_client = AsyncOpenAI(
            base_url=openai_base_url,
            api_key=openai_api_key,
            http_client=AsyncClient(proxy=proxy),
        )

    async def pick(
        self,
        image: io.BytesIO,
        category: Optional[GarbageCategory] = None,
    ):
        await asyncio.sleep(5)
        return {"swgdrhf", "wy4ew"}


advice_picker = AdvicePicker(
    openai_base_url=SETTINGS.OPENAI_API_BASE,
    openai_api_key=SETTINGS.OPENAI_API_KEY.get_secret_value(),
    proxy=(
        SETTINGS.HTTP_PROXY_SERVER.get_secret_value()
        if SETTINGS.HTTP_PROXY_SERVER
        else None
    ),
)
