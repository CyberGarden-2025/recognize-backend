import os
import tempfile
from pyzxing import BarCodeReader
from pydantic import BaseModel


class QrResult(BaseModel):
    type: str
    data: str


def scan_codes(image_path: str) -> list[QrResult]:
    reader = BarCodeReader()

    try:
        result = reader.decode(image_path)
    except Exception:
        return []

    if not result:
        return []

    codes: list[QrResult] = []

    for obj in result:
        if not isinstance(obj, dict):
            continue

        fmt = obj.get("format")
        raw = obj.get("parsed") or obj.get("raw")

        if isinstance(fmt, bytes):
            fmt = fmt.decode("utf-8", errors="ignore")

        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="ignore")

        if not fmt or not raw:
            continue

        codes.append(QrResult(type=fmt, data=raw))

    return codes


def scan_codes_image_bytes(image_bytes: bytes) -> list[QrResult]:
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    fname = tmp.name
    tmp.write(image_bytes)
    tmp.close()

    try:
        result = scan_codes(tmp.name)
    finally:
        os.unlink(fname)
    return result
