import torch
import matplotlib.pyplot as plt
from torchvision import datasets, transforms
from cnn import SudokuCNN

def evaluate():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluating on device: {device}")
    
    transform = transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=10, shuffle=True)
    
    model = SudokuCNN().to(device)
    model.load_state_dict(torch.load('weights.pt'))
    model.eval()
    
    dataiter = iter(test_loader)
    images, labels = next(dataiter)
    images, labels = images.to(device), labels.to(device)
    
    with torch.no_grad():
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)
        
    print("-" * 30)
    print(f"Actual labels:    {labels.tolist()[:10]}")
    print(f"Predicted labels: {predicted.tolist()[:10]}")
    print("-" * 30)
    
    correct = (predicted == labels).sum().item()
    print(f"Batch Accuracy: {correct / len(labels) * 100:.2f}%")
    
    # Plotting the images
    images = images.cpu()
    fig, axes = plt.subplots(2, 5, figsize=(10, 5))
    for i, ax in enumerate(axes.flatten()):
        # Unnormalize image for display
        img = images[i].squeeze() * 0.5 + 0.5
        ax.imshow(img, cmap='gray')
        ax.axis('off')
        color = 'green' if predicted[i] == labels[i] else 'red'
        ax.set_title(f"Pred: {predicted[i].item()}\nAct: {labels[i].item()}", color=color)
        
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    evaluate()