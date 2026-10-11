import cv2
import numpy as np
import os
import torch
from model.cnn import SudokuCNN
import matplotlib.pyplot as plt

# Load the trained model
sudoku_cnn = SudokuCNN()
sudoku_cnn.eval()

# Ensure the model is on the same device as the input
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sudoku_cnn.to(device)

# Function to preprocess the image and evaluate the model
def preprocess_image(image_path: str, output_dir: str) -> list:
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read the image
    img = cv2.imread(image_path)
    
    if img is None:
        raise FileNotFoundError(f"The image file {image_path} could not be found or opened.")
    
    # Grayscale conversion
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Remove grid lines using Canny edge detection and hough lines
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(gray, (x1, y1), (x2, y2), (0, 0, 0), 2)
    
    # Resize the Sudoku region to a 288x288 grid (9x9 cells, each 32x32)
    resized_sudoku_region = cv2.resize(gray, (288, 288))
    
    # Split the Sudoku grid into 9x9 cells
    cells = []
    for i in range(9):
        for j in range(9):
            cell = resized_sudoku_region[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32]
            cells.append(cell)
    
    # Process each cell and collect predictions
    predictions = []
    for cell in cells:
        input_tensor = torch.tensor(cell).unsqueeze(0).unsqueeze(0).float().to(device)
        with torch.no_grad():
            output = sudoku_cnn(input_tensor)
            _, predicted = torch.max(output, 1)
            predictions.append(predicted.item())
    
    return predictions

# Function to split the Sudoku board into 81 images
def split_sudoku_board(image_path: str, output_dir: str):
    # Read the image
    img = cv2.imread(image_path)
    
    if img is None:
        raise FileNotFoundError(f"The image file {image_path} could not be found or opened.")
    
    # Grayscale conversion
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Remove grid lines using Canny edge detection and hough lines
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    
    if lines is not None:
        for line in lines:
            if len(line) != 1:
                continue
            x1, y1, x2, y2 = line[0]
            cv2.line(gray, (x1, y1), (x2, y2), (0, 0, 0), 2)
    
    # Resize the Sudoku region to a 288x288 grid (9x9 cells, each 32x32)
    resized_sudoku_region = cv2.resize(gray, (288, 288))
    
    # Split the Sudoku grid into 9x9 cells
    cells = []
    for i in range(9):
        for j in range(9):
            cell = resized_sudoku_region[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32]
            cells.append(cell)
    
    # Save each cell as an image
    for i, cell in enumerate(cells):
        cell_path = os.path.join(output_dir, f"cell_{i + 1}.png")
        cv2.imwrite(cell_path, cell)
    
    return cells

# Example usage
if __name__ == "__main__":
    image_path = 'sudoku_test.png'
    output_dir = 'output_cells'
    
    # Split the Sudoku board into 81 images
    split_sudoku_board(image_path, output_dir)
    
    # Preprocess each cell and collect predictions
    predictions = preprocess_image(image_path, output_dir)
    
    # Print the predictions in a 9x9 grid format
    for i in range(9):
        for j in range(9):
            print(f"Cell [{i + 1}, {j + 1}]: {predictions[i * 9 + j]}")
        print()