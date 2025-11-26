# model_service.py

import os, json, torch, torch.nn as nn, torchvision.models as models, torchvision.transforms as T
import kornia.augmentation as K
from PIL import Image
from typing import List, Tuple

# Config
MODEL_PATH = os.getenv("MODEL_PATH", r"bestfood101_res50.pth")
CLASS_NAMES_PATH = os.getenv("CLASS_NAMES_PATH", r"food101_class_names.json")
NUM_CLASSES = int(os.getenv("NUM_CLASSES", "101"))
IMG_SIZE = int(os.getenv("IMG_SIZE", "224"))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load class names
with open(CLASS_NAMES_PATH, 'r') as f:
    class_names = {int(k): v for k, v in json.load(f).items()}

# Transforms
cpu_transform = T.Compose([
    T.Resize((IMG_SIZE, IMG_SIZE)),
    T.ToTensor(),
])
gpu_normalize = nn.Sequential(
    K.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
).to(device)

# Model builder
def build_resnet50(num_classes: int) -> nn.Module:
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model

# Load model
def load_model() -> nn.Module:
    print(f"Loading ResNet50 model from checkpoint: {MODEL_PATH}")
    ckpt = torch.load(MODEL_PATH, map_location='cpu')
    if isinstance(ckpt, dict) and 'state_dict' in ckpt:
        state_dict = ckpt['state_dict']
    else:
        state_dict = ckpt
    state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}
    model = build_resnet50(NUM_CLASSES)
    model.load_state_dict(state_dict, strict=False)
    model = model.to(device)
    model.eval()
    return model

# Prediction
def predict_topk(model: nn.Module, image: Image.Image, topk: int = 5) -> List[Tuple[str, float]]:
    tensor = cpu_transform(image)
    batch = tensor.unsqueeze(0).to(device)
    with torch.no_grad():
        with torch.cuda.amp.autocast(enabled=(device.type == 'cuda')):
            normalized = gpu_normalize(batch)
            outputs = model(normalized)
            probs = torch.nn.functional.softmax(outputs[0], dim=0)
    topk_probs, topk_idx = torch.topk(probs, k=topk)
    return [(class_names.get(int(idx), f"Class_{idx}"), float(prob)) for prob, idx in zip(topk_probs, topk_idx)]