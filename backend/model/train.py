import os
import random
from PIL import Image, ImageDraw, ImageFont
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import datasets, transforms
from cnn import SudokuCNN

class SudokuDataset(Dataset):
    def __init__(self, mnist_dataset, num_synthetic=5000):
        self.mnist = mnist_dataset
        self.synthetic_samples = []
        
        # Generate synthetic printed digits to bridge the domain gap
        print("Generating synthetic printed font samples...")
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        except IOError:
            font = ImageFont.load_default()
            
        for _ in range(num_synthetic):
            digit = random.randint(0, 9)
            # Create a 32x32 white canvas
            img = Image.new("L", (32, 32), 255)
            draw = ImageDraw.Draw(img)
            
            # Add minor random offsets for variation
            x = random.randint(4, 10)
            y = random.randint(2, 8)
            draw.text((x, y), str(digit), fill=0, font=font)
            
            # Apply same tensor transforms as MNIST
            tensor_img = transforms.functional.to_tensor(img)
            normalized_img = transforms.functional.normalize(tensor_img, (0.5,), (0.5,))
            self.synthetic_samples.append((normalized_img, digit))
            
    def __len__(self):
        return len(self.mnist) + len(self.synthetic_samples) + 2000
        
    def __getitem__(self, idx):
        if idx < len(self.mnist):
            image, label = self.mnist[idx]
            if label == 0:
                label = 9  # Map MNIST 0 if needed for your label schema
            return image, label
        elif idx < len(self.mnist) + len(self.synthetic_samples):
            return self.synthetic_samples[idx - len(self.mnist)]
        else:
            # Synthetic blank cell noise
            blank_image = torch.randn(1, 32, 32) * 0.05
            return blank_image, 0

class EarlyStopping:
    def __init__(self, patience=5, verbose=False):
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False

    def __call__(self, val_loss, model):
        score = val_loss
        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        elif score > self.best_score:
            self.counter += 1
            print(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        if self.verbose:
            print(f'Validation loss decreased ({self.best_score:.4f} --> {val_loss:.4f}). Saving model ...')
        weights_path = os.path.join(os.path.dirname(__file__), 'weights.pt')
        torch.save(model.state_dict(), weights_path)

def train():
    transform = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(10),
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    
    print("Downloading MNIST dataset...")
    base_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    
    dataset = SudokuDataset(base_dataset)
    
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    print(f"Using device: {device}")

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=128, shuffle=False)
    
    model = SudokuCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=3, factor=0.1)

    epochs = 20
    print(f"Starting training for {epochs} epochs...")
    early_stopping = EarlyStopping(patience=5, verbose=True)

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {running_loss/len(train_loader):.4f} | Val Loss: {val_loss/len(val_loader):.4f}")

        early_stopping(val_loss, model)
        if early_stopping.early_stop:
            print("Early stopping triggered.")
            break
            
        scheduler.step(val_loss)

    print("Training complete. Weights saved to weights.pt.")

if __name__ == '__main__':
    train()