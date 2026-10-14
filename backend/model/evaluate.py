import os
import torch
from torchvision import datasets, transforms
from cnn import SudokuCNN

def evaluate():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluating on device: {device}")
    
    # Load model weights using a robust path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    weights_path = os.path.join(base_dir, "weights.pt")
    
    model = SudokuCNN().to(device)
    if os.path.exists(weights_path):
        # Fixed: call load_state_dict on the instance 'model', not the class 'SudokuCNN'
        model.load_state_dict(torch.load(weights_path, map_location=device))
        print(f"Successfully loaded weights from {weights_path}")
    else:
        print(f"Warning: Weights file not found at {weights_path}. Model is running on uninitialized weights.")
    model.eval()
    
    # Use deterministic transforms for evaluation (no random flips/rotations)
    transform = transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    
    test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=100, shuffle=False)
    
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    print(f"Accuracy of the model on the 10000 test images: {100 * correct / total:.2f}%")

if __name__ == '__main__':
    evaluate()