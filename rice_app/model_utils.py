from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

# ต้องตรงกับ full_train_ds.classes ในโน้ตบุ๊ก
CLASSES = ["arborio", "basmati", "ipsala", "jasmine", "karacadag"]

MODEL_PATH = Path(__file__).parent / "models" / "DenseNet121" / "best_model_fold3.pt"

# เหมือนตอนฝึก: ไม่มี Normalize
TRANSFORM = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])


def load_model(path: Path = MODEL_PATH) -> nn.Module:
    model = models.densenet121(weights=None)
    model.classifier = nn.Linear(model.classifier.in_features, len(CLASSES))
    state = torch.load(path, map_location="cpu", weights_only=True)
    # รองรับโมเดลที่เซฟจาก DataParallel
    state = {k.removeprefix("module."): v for k, v in state.items()}
    model.load_state_dict(state)
    model.eval()
    return model


@torch.no_grad()
def predict(model: nn.Module, images: list[Image.Image]) -> torch.Tensor:
    batch = torch.stack([TRANSFORM(img.convert("RGB")) for img in images])
    return torch.softmax(model(batch), dim=1)
