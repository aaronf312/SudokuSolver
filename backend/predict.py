import numpy as np
import torch
from torchvision import transforms
from PIL import Image
from model.cnn import SudokuCNN

def predict_image(image_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluating on device: {device}")
    
    # Define transformations for testing
    transform = transforms.Compose([
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    
    try:
        image = Image.open(image_path).convert('L')  # Convert to grayscale
        image = transform(image).unsqueeze(0)  # Add batch dimension
        image = image.to(device)
        
        model = SudokuCNN().to(device)
        model.eval()
        
        with torch.no_grad():
            outputs = model(image)
            _, predicted = torch.max(outputs, 1)
            predicted_digit = predicted.item()
            
            print(f"Original image shape: {image.shape[2:]}")
            print(f"Resized image shape: (32, 32)")
            print(f"Normalized image min: {image.min()}, max: {image.max()}")
            print(f"Predicted digit: {predicted_digit}")
            
            return predicted_digit
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

if __name__ == '__main__':
    image_paths = [
        'number.png',

    ]
    
    for image_path in image_paths:
        predict_image(image_path)