"""
Qon guruhi modeli o'rgatish
Ishlatish: python train.py
"""
import os, time
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torchvision.models import ResNet18_Weights
from torch.utils.data import DataLoader, random_split

DATASET_DIR = os.path.join(os.path.dirname(__file__), 'dataset')
MODEL_DIR   = os.path.join(os.path.dirname(__file__), 'model')
MODEL_PATH  = os.path.join(MODEL_DIR, 'blood_group_model.pth')

IMG_SIZE    = 128
BATCH_SIZE  = 32
EPOCHS      = 20
LR          = 0.001
TRAIN_SPLIT = 0.8

os.makedirs(MODEL_DIR, exist_ok=True)

def main():
    
    transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.Grayscale(num_output_channels=3),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    ])

    print(f"\n📂 Dataset yuklanmoqda: {DATASET_DIR}")
    dataset     = datasets.ImageFolder(root=DATASET_DIR, transform=transform)
    class_names = dataset.classes
    print(f"   Sinflar: {class_names}")
    print(f"   Jami rasmlar: {len(dataset)}")

    train_size = int(TRAIN_SPLIT * len(dataset))
    test_size  = len(dataset) - train_size
    train_ds, test_ds = random_split(dataset, [train_size, test_size])
    print(f"   Train: {train_size}  |  Test: {test_size}\n")

 
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=0)
    test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    if torch.cuda.is_available():
        device = torch.device("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        print(f"⚡ GPU topildi: {gpu_name}")
    else:
        device = torch.device("cpu")
        print(f"⚙  Qurilma: CPU (GPU topilmadi)")

    model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(model.fc.in_features, len(class_names))
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    best_acc = 0.0
    print(f"🚀 O'rgatish boshlanmoqda... ({EPOCHS} epoch)\n")

    for epoch in range(EPOCHS):
        t0 = time.time()
        model.train()
        running_loss = correct = total = 0

        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            out  = model(imgs)
            loss = criterion(out, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, pred = torch.max(out, 1)
            total   += labels.size(0)
            correct += (pred == labels).sum().item()

        scheduler.step()
        acc     = 100 * correct / total
        elapsed = time.time() - t0

 
        model.eval()
        v_correct = v_total = 0
        with torch.no_grad():
            for imgs, labels in test_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                out = model(imgs)
                _, pred = torch.max(out, 1)
                v_total   += labels.size(0)
                v_correct += (pred == labels).sum().item()
        val_acc = 100 * v_correct / v_total

        print(f"Epoch [{epoch+1:02d}/{EPOCHS}]  "
              f"Loss: {running_loss/len(train_loader):.4f}  "
              f"Train: {acc:.1f}%  Val: {val_acc:.1f}%  "
              f"({elapsed:.1f}s)")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'class_names':      class_names,
                'val_accuracy':     val_acc,
            }, MODEL_PATH)
            print(f"          💾 Model saqlandi (val_acc={val_acc:.1f}%)")

    print(f"\n✅ Eng yaxshi val aniqlik: {best_acc:.1f}%")
    print(f"📦 Model: {MODEL_PATH}\n")


if __name__ == '__main__':
    main()