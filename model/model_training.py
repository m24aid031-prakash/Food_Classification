import os
import torch
from torch.utils.data import DataLoader
import torchvision.transforms as T
import torchvision.datasets as datasets
import torchvision.models as models
import torch.nn as nn
import torch.optim as optim
from typing import Tuple
import tqdm
import kornia.augmentation as K
import kornia.geometry.transform as KT
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from torchvision.transforms import ToTensor
import pathlib
from PIL import Image

# -----------------------
# Configuration
# -----------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Script's directory for relative paths
DATASET_PATH = os.path.join(SCRIPT_DIR, "data", "food-101")  # Relative path
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "64"))
NUM_EPOCHS = int(os.getenv("EPOCHS", "20"))
VAL_SPLIT = float(os.getenv("VAL_SPLIT", "0.15"))
EARLY_STOP_PATIENCE = int(os.getenv("EARLY_STOP_PATIENCE", "0"))
BEST_MODEL_PATH = os.path.join(SCRIPT_DIR, "bestfood101_res50.pth")  # Relative path
FINAL_MODEL_PATH = os.path.join(SCRIPT_DIR, "finfood101_res50.pth")  # Relative path
LR = float(os.getenv("LR", "0.0002"))
MODEL_NAME = os.getenv("MODEL_NAME", "resnet50")
IMG_SIZE = int(os.getenv("IMG_SIZE", "224"))
AUTO_SCALE_BATCH = os.getenv("AUTO_SCALE_BATCH", "0") == "1"
TARGET_UTILIZATION = float(os.getenv("TARGET_GPU_UTIL", "0.97"))

# Num workers for DataLoader: change as needed after you verify pipeline
NUM_WORKERS = min(6, os.cpu_count() or 1)

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# -----------------------
# Top-level helpers (picklable)
# -----------------------
def pil_to_rgb(img: Image.Image) -> Image.Image:
    """Convert PIL image to RGB (top-level function so it's picklable)."""
    return img.convert("RGB")

# CPU transforms (resize + to tensor) - deterministic and consistent shapes
cpu_transform = T.Compose([
    T.Lambda(pil_to_rgb),
    T.Resize((IMG_SIZE, IMG_SIZE)),
    ToTensor(),  # outputs CxHxW floats in [0,1]
])

# -----------------------
# Evaluation helper
# -----------------------
def evaluate(model: nn.Module, val_loader: DataLoader, val_aug_pipeline: nn.Module, criterion) -> Tuple[float, float]:
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device, non_blocking=True if device.type == 'cuda' else False)
            labels = labels.to(device, non_blocking=True if device.type == 'cuda' else False)
            with torch.cuda.amp.autocast(enabled=torch.cuda.is_available()):
                images = val_aug_pipeline(images)
                outputs = model(images)
                loss = criterion(outputs, labels)
            total_loss += loss.item() * labels.size(0)
            preds = outputs.argmax(1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    avg_loss = total_loss / total if total else 0.0
    acc = correct / total if total else 0.0
    return avg_loss, acc

def report_gpu(prefix=""):
    if torch.cuda.is_available():
        alloc = torch.cuda.memory_allocated() / (1024**2)
        reserved = torch.cuda.memory_reserved() / (1024**2)
        total = torch.cuda.get_device_properties(0).total_memory / (1024**2)
        print(f"{prefix}GPU Memory | allocated={alloc:.1f}MB reserved={reserved:.1f}MB total={total:.0f}MB util={(reserved/total)*100:.1f}%")
    else:
        print(f"{prefix}No GPU available. Running on CPU.")

# -----------------------
# MAIN: dataset, model, training
# -----------------------
if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()

    # Decide image folder root:
    # If path/images exists (Food-101 style), use that. Otherwise use the path itself.
    p = pathlib.Path(DATASET_PATH)
    images_subdir = p / "images"
    if images_subdir.exists() and images_subdir.is_dir():
        image_root = str(images_subdir)
    else:
        image_root = str(p)

    # Ensure path exists
    if not pathlib.Path(image_root).exists():
        raise FileNotFoundError(f"Image directory not found: {image_root}")

    # Create dataset via ImageFolder; ImageFolder expects subfolders per class
    dataset_all = datasets.ImageFolder(root=image_root, transform=cpu_transform)
    full_len = len(dataset_all)
    if full_len == 0:
        raise RuntimeError(f"No images found under {image_root}")

    # Split into train/val
    val_len = int(full_len * VAL_SPLIT)
    train_len = full_len - val_len
    train_dataset, val_dataset = torch.utils.data.random_split(dataset_all, [train_len, val_len], generator=torch.Generator().manual_seed(42))
    print(f"Loaded images from {image_root}: total={full_len} train={train_len} val={val_len}")

    # DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=NUM_WORKERS, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, pin_memory=True)

    # Model setup
    NUM_CLASSES = 101
    if "mobilenetv3" in MODEL_NAME.lower():
        model = models.mobilenet_v3_large(pretrained=True)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, NUM_CLASSES)
        print(f"Initialized MobileNetV3_Large with {NUM_CLASSES} classes.")
    else:
        model = models.resnet50(pretrained=True)
        model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
        print(f"Initialized ResNet50 with {NUM_CLASSES} classes.")

    model = model.to(device)

    # GPU Kornia pipelines (augment + normalize). Resize already done on CPU.
    train_aug_pipeline = nn.Sequential(
        K.RandomHorizontalFlip(p=0.5),
        K.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.1, p=0.8),
        K.RandomRotation(degrees=10.0, p=0.5),
        K.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ).to(device)

    val_aug_pipeline = nn.Sequential(
        K.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ).to(device)

    # Optimizer / scheduler / scaler / criterion
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=LR)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS)
    scaler = torch.cuda.amp.GradScaler(enabled=torch.cuda.is_available())

    # Quick smoke test: fetch one batch
    try:
        bimg, blabel = next(iter(train_loader))
        print("Smoke test batch shapes:", bimg.shape, blabel.shape, bimg.dtype)
    except Exception as e:
        print("Smoke test failed:", e)
        raise

    # Training loop
    best_acc = 0.0
    best_epoch = -1
    epochs_no_improve = 0
    history = []

    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True

    report_gpu("Before training: ")
    for epoch in range(1, NUM_EPOCHS + 1):
        model.train()
        running_loss = 0.0

        pbar = tqdm.tqdm(train_loader, desc=f"Epoch {epoch}/{NUM_EPOCHS} Training")
        for batch_idx, (images, labels) in enumerate(pbar):
            images = images.to(device, non_blocking=True if device.type == 'cuda' else False)
            labels = labels.to(device, non_blocking=True if device.type == 'cuda' else False)

            optimizer.zero_grad(set_to_none=True)
            with torch.cuda.amp.autocast(enabled=torch.cuda.is_available()):
                images = train_aug_pipeline(images)
                outputs = model(images)
                loss = criterion(outputs, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            running_loss += loss.item()
            pbar.set_postfix({'Loss': f'{loss.item():.4f}'})

        avg_train_loss = running_loss / max(1, (batch_idx + 1))
        scheduler.step()

        report_gpu(f"Epoch {epoch} end: ")
        val_loss, val_acc = evaluate(model, val_loader, val_aug_pipeline, criterion)

        current_lr = optimizer.param_groups[0]['lr']
        print(f"Epoch {epoch}/{NUM_EPOCHS} LR {current_lr:.6f} TrainLoss {avg_train_loss:.4f} ValLoss {val_loss:.4f} ValAcc {val_acc*100:.2f}%")

        history.append({
            'epoch': epoch,
            'train_loss': avg_train_loss,
            'val_loss': val_loss,
            'val_acc': val_acc,
            'lr': current_lr
        })

        if val_acc > best_acc:
            best_acc = val_acc
            best_epoch = epoch
            torch.save({
                'epoch': epoch,
                'model_state': model.state_dict(),
                'optimizer_state': optimizer.state_dict(),
                'scaler_state': scaler.state_dict(),
                'val_acc': best_acc,
            }, BEST_MODEL_PATH)
            print(f"New best model (acc={best_acc*100:.2f}%) saved to {BEST_MODEL_PATH}")
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1

        if EARLY_STOP_PATIENCE > 0 and epochs_no_improve >= EARLY_STOP_PATIENCE:
            print(f"Early stopping triggered after {epoch} epochs. Best epoch {best_epoch} acc {best_acc*100:.2f}%")
            break

    torch.save(model.state_dict(), FINAL_MODEL_PATH)
    print(f"Final model weights saved to {FINAL_MODEL_PATH}. Best acc {best_acc*100:.2f}% at epoch {best_epoch}")

    # Save history & plot
    if history:
        df_history = pd.DataFrame(history)
        history_path = os.path.join(SCRIPT_DIR, 'training_history.xlsx')  # Relative path
        df_history.to_excel(history_path, index=False)
        plt.figure(figsize=(10, 6))
        plt.plot(df_history['epoch'], df_history['train_loss'], label='Training Loss', marker='o')
        plt.plot(df_history['epoch'], df_history['val_loss'], label='Validation Loss', marker='x')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training and Validation Loss per Epoch')
        plt.legend()
        plt.grid(True)
        plot_path = os.path.join(SCRIPT_DIR, 'loss_plot.png')  # Relative path
        plt.savefig(plot_path)
        print(f"History saved to {history_path}, plot to {plot_path}")
