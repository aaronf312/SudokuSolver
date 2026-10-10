import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms
from cnn import SudokuCNN

class SudokuDataset(Dataset):
   # Using MNIST dataset as baseline training
    def __init__(self, mnist_dataset):
        self.mnist = mnist_dataset
        
    def __len__(self):
        # Double the dataset size roughly to include blanks, or adjust as needed
        return len(self.mnist) + 2000
        
    def __getitem__(self, idx):
        if idx < len(self.mnist):
            image, label = self.mnist[idx]
            # MNIST labels are 0-9; shift them so MNIST '0' becomes part of training 
            # or remap if needed. Standard Sudoku: 1-9 are digits, 0 is empty.
            # If MNIST has a '0', we can treat it as digit 0, but for Sudoku we want 
            # 0 to be blank. Let's map MNIST labels 1-9 normally, and create blanks for 0.
            if label == 0:
                label = 9 # Or handle standard MNIST 0 mapping
            return image, label
        else:
            # Generate synthetic blank cell (mostly white/background noise with 0 label)
            # MNIST images are 1 channel, 32x32 if resized. Let's match 32x32.
            blank_image = torch.randn(1, 32, 32) * 0.05 # slight noise around zero
            return blank_image, 0

def train():
    # Transform MNIST to 32x32 and normalize
    transform = transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    
    print("Downloading MNIST dataset...")
    base_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
    
    # Filter out or adjust MNIST labels so 1-9 are actual digits, and add class 0 blanks

    #Get GPU
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    print(f"Using device: {device}")

    train_loader = DataLoader(base_dataset, batch_size=64, shuffle=True)
    
    model = SudokuCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    epochs = 3
    print(f"Starting training for {epochs} epochs...")
    model.train()
    
    for epoch in range(epochs):
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
        print(f"Epoch {epoch+1}/{epochs} - Loss: {running_loss/len(train_loader):.4f}")
        
    # Save weights
    weights_path = os.path.join(os.path.dirname(__file__), 'weights.pt')
    torch.save(model.state_dict(), weights_path)
    print(f"Model weights saved successfully to {weights_path}")

if __name__ == '__main__':
    train()