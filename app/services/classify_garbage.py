import torch
from PIL import Image
from enum import Enum
from io import BytesIO
from torch import Tensor
from torchvision.transforms import v2 as v2_transforms
from efficientnet_pytorch import EfficientNet


class GarbageCategory(str, Enum):
    Cardboard = "Cardboard"
    Glass = "Glass"
    Metal = "Metal"
    Paper = "Paper"
    Plastic = "Plastic"
    Trash = "Trash"


LABELS = [
    GarbageCategory.Cardboard.value,
    GarbageCategory.Glass.value,
    GarbageCategory.Metal.value,
    GarbageCategory.Paper.value,
    GarbageCategory.Plastic.value,
    GarbageCategory.Trash.value,
]
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODEL: EfficientNet = torch.load(
    "ml_models/garbage_classification.pth", map_location="cpu", weights_only=False
)
MODEL = MODEL.to(DEVICE)

TRANSFORM = v2_transforms.Compose(
    [
        v2_transforms.ToImage(),
        v2_transforms.ToDtype(torch.float32, scale=True),
    ]
)


def classify_garbage(image_path: str | BytesIO) -> GarbageCategory:
    image = Image.open(image_path).convert("RGB").resize((224, 224))
    image: Tensor = TRANSFORM(image)
    image = image.unsqueeze(0)

    image = image.to(DEVICE)
    MODEL.eval()

    with torch.no_grad():
        logits = MODEL(image)
    _, predicted = torch.max(logits, 1)

    return GarbageCategory(LABELS[predicted])
