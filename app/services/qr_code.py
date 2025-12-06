from pyzbar.pyzbar import decode, Decoded
from pydantic import BaseModel
from PIL import Image


class QrResult(BaseModel):
    type: str
    data: str


def scan_codes(image_path: str) -> list[QrResult]:
    img = Image.open(image_path)
    result: list[Decoded] = decode(img)
    codes = []

    for obj in result:
        codes.append(QrResult(type=obj.type, data=obj.data.decode()))

    return codes
