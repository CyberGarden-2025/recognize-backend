import base64
from typing import Optional

from httpx import AsyncClient
from httpx._types import ProxyTypes
from openai import AsyncOpenAI

from app.schemas.gatbage import (
    GarbageType,
    GarbageSubtype,
    GarbageState,
    GarbageData,
    GarbageDataList,
)
from .llm_utils import optimize_for_openai
from app.settings import SETTINGS


class GarbageClassifier:
    def __init__(
        self,
        openai_base_url: str,
        openai_api_key: str,
        openai_gpt_model: str,
        proxy: Optional[ProxyTypes] = None,
    ):
        self.openai_gpt_model = openai_gpt_model
        self.openai_client = AsyncOpenAI(
            base_url=openai_base_url,
            api_key=openai_api_key,
            http_client=AsyncClient(proxy=proxy),
        )

    @staticmethod
    def merge_garbage_items(items: list[GarbageData]) -> list[GarbageData]:
        unique = {}

        for item in items:
            key = (item.type.value, item.subtype.value, item.state.value)

            if key not in unique:
                unique[key] = item

        return list(unique.values())

    async def classify(self, image: bytes):
        system_prompt = (
            f"""
Ты система классификации отходов.
Твоя задача - строго по изображению определить тип, подтип и состояние каждого визуально различимого элемента.
Опирайся только на то, что видно на фото. Не придумывай ничего, что невозможно подтвердить визуально.
Если на изображении несколько частей одного предмета (например: стакан и крышка, бутылка и крышка, коробка и пластиковое окно), классифицируй каждую часть отдельно и верни массив объектов.
Всегда возвращай массив, даже если объект один.

Ты обязан формировать ответ строго как JSON object, содержащий единственное поле "items". Поле "items" должно быть массивом объектов. Каждый объект должен содержать поля type, subtype, state.

Поле type должно содержать одно из следующих значений: {", ".join([item.value for item in GarbageType])}. **Любое другое значение запрещено.**
Поле subtype должно содержать одно из следующих значений: {", ".join([item.value for item in GarbageSubtype])}. **Любое другое значение запрещено.**
Поле state должно содержать одно из следующих значений: {", ".join([item.value for item in GarbageState])}. **Любое другое значение запрещено.**

Если нет уверенности, subtype и state должны быть "unknown". Если объект не подходит ни под одну категорию type, используй type="Trash" и subtype="unknown".

Используй следующие правила для выбора subtype:
PET: прозрачные пищевые бутылки — pet_bottle; белые непрозрачные — pet_bottle_white; контейнеры и стаканы из PET — pet_container; бутылки из-под масла или загрязнённые органикой — pet_bottle с состоянием dirty или food_contaminated.
HDPE: ёмкости любого цвета — hdpe_container; плотная плёнка и пупырка — hdpe_film; плотные пакеты — hdpe_bag.
PP: твёрдые ёмкости — pp_container; крупные ёмкости (тазы, вёдра) — pp_large; пакеты PP — pp_bag; если есть термоусадочная плёнка или не снятые наклейки — state with_labels.
Пенопласт: упаковочный — foam_packaging; строительный — foam_building; ячейки для яиц — foam_egg; пенопласт из-под еды — foam_food.
Другие пластики: blister_pack, toothbrush, plastic_card, tube; чеки как receipt.

Всегда строго соблюдай JSON-структуру: """
            + """ { "items": [ { "type": "...", "subtype": "...", "state": "..." } ] }

Никакого текста, комментариев, рассуждений, объяснений или форматирования вне JSON не допускается.
""".strip()
        )

        optimized_image = optimize_for_openai(image)
        base64_image = base64.b64encode(optimized_image).decode("utf-8")

        response = await self.openai_client.chat.completions.create(
            model=self.openai_gpt_model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        }
                    ],
                },
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if content is None:
            raise Exception

        content = content.removeprefix("```json\n").removesuffix("\n```")
        result = GarbageDataList.model_validate_json(content)

        result.items = self.merge_garbage_items(result.items)
        return result


garbage_classifier = GarbageClassifier(
    openai_base_url=SETTINGS.OPENAI_API_BASE,
    openai_api_key=SETTINGS.OPENAI_API_KEY.get_secret_value(),
    openai_gpt_model=SETTINGS.OPENAI_GPT_MODEL,
    proxy=(
        SETTINGS.HTTP_PROXY_SERVER.get_secret_value()
        if SETTINGS.HTTP_PROXY_SERVER
        else None
    ),
)
