import io

import tiktoken
from PIL import Image

tokenizer = tiktoken.encoding_for_model("gpt-4o")


def count_tokens(messages: list[str]):
    return sum(len(tokenizer.encode(m)) for m in messages)


def optimize_for_openai(image_bytes: bytes) -> bytes:
    # Максимальный размер для детального анализа
    target_max_size = 200
    format = "JPEG"

    buffer = io.BytesIO(image_bytes)
    with Image.open(buffer) as img:
        original_width, original_height = img.size

        # Определяем базовые параметры на основе исходного размера
        if max(original_width, original_height) > 4000:  # 4K+
            scale_factor = 0.3
            quality = 85
        elif max(original_width, original_height) > 2000:  # HD+
            scale_factor = 0.5
            quality = 85
        else:  # Меньше HD
            scale_factor = 0.8
            quality = 90

        # Рассчитываем новые размеры
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Ограничиваем максимальный размер
        if max(new_width, new_height) > target_max_size:
            if new_width > new_height:
                scale_factor = target_max_size / original_width
            else:
                scale_factor = target_max_size / original_height

            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)

        # Конвертируем в RGB если нужно
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Сохраняем в байты
        output_buffer = io.BytesIO()
        resized_img.save(output_buffer, format=format, quality=quality, optimize=True)
        return output_buffer.getvalue()
