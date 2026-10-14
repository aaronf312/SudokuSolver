import os
import cv2
import numpy as np
import torch
import matplotlib.pyplot as plt
from model.cnn import SudokuCNN

# Initialize model, load weights, and set to evaluation mode
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sudoku_cnn = SudokuCNN()

base_dir = os.path.dirname(os.path.abspath(__file__))
weights_path = os.path.join(base_dir, "model", "weights.pt")

if os.path.exists(weights_path):
    sudoku_cnn.load_state_dict(torch.load(weights_path, map_location=device))
    print(f"Successfully loaded weights from {weights_path}")
else:
    print(f"Warning: Weights file not found at {weights_path}. Model is running on uninitialized weights.")

sudoku_cnn.eval()
sudoku_cnn.to(device)

def classify_cell(cell):
    """Normalizes a single cell tensor and runs inference."""
    cell_normalized = cell.astype(np.float32) / 255.0
    input_tensor = torch.tensor(cell_normalized).unsqueeze(0).unsqueeze(0).to(device)
    with torch.no_grad():
        output = sudoku_cnn(input_tensor)
        _, predicted = torch.max(output, 1)
        return predicted.item()

def process_cell(raw_cell):
    """Clears borders via flood-fill, filters out corner fragments, and centers the digit on a white 32x32 canvas."""
    h, w = raw_cell.shape
    
    # Minimal 1px trim just to detach any edge-hugging noise
    pad = 1
    if h > pad * 2 and w > pad * 2:
        raw_cell = raw_cell[pad:h-pad, pad:w-pad]
        h, w = raw_cell.shape
        
    # Invert to work with white text on black background for flood-fill
    inv = cv2.bitwise_not(raw_cell)
    
    # Flood-fill from outer borders to wipe out connected grid lines
    flood_filled = inv.copy()
    mask = np.zeros((h + 2, w + 2), np.uint8)
    
    for x in range(w):
        if flood_filled[0, x] > 0:
            cv2.floodFill(flood_filled, mask, (x, 0), 0)
        if flood_filled[h-1, x] > 0:
            cv2.floodFill(flood_filled, mask, (x, h-1), 0)
    for y in range(h):
        if flood_filled[y, 0] > 0:
            cv2.floodFill(flood_filled, mask, (0, y), 0)
        if flood_filled[y, w-1] > 0:
            cv2.floodFill(flood_filled, mask, (w-1, y), 0)
            
    # Invert back to black digits on white background
    cleaned_cell = cv2.bitwise_not(flood_filled)
    
    # Find contours of the remaining elements
    inv_cleaned = cv2.bitwise_not(cleaned_cell)
    contours, _ = cv2.findContours(inv_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    blank_cell = np.ones((32, 32), dtype=np.uint8) * 255
    if not contours:
        return blank_cell
        
    # Filter out corner brackets and noise fragments
    valid_contours = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 30:  
            continue
        x, y, cw, ch = cv2.boundingRect(c)
        
        # Reject very thin vertical strips (like residual grid lines)
        aspect_ratio = float(cw) / ch
        if aspect_ratio > 3.5 or (aspect_ratio < 0.15 and ch < 20):
            continue
            
        if cw < 4 or ch < 6:
            continue
            
        valid_contours.append((c, area))
        
    if not valid_contours:
        return blank_cell
        
    largest_contour = max(valid_contours, key=lambda x: x[1])[0]
    
    # Get bounding box of the actual digit
    x, y, cw, ch = cv2.boundingRect(largest_contour)
    digit_crop = cleaned_cell[y:y+ch, x:x+cw]
    
    # Resize keeping aspect ratio, target max dimension of 20 pixels
    scale = 20.0 / max(ch, cw)
    new_h, new_w = int(ch * scale), int(cw * scale)
    if new_h <= 0 or new_w <= 0:
        return blank_cell
        
    resized_digit = cv2.resize(digit_crop, (new_w, new_h))
    
    # Paste centered onto a 32x32 WHITE canvas (255)
    canvas = np.ones((32, 32), dtype=np.uint8) * 255
    y_offset = (32 - new_h) // 2
    x_offset = (32 - new_w) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_digit
    
    return canvas

def save_and_display_cells(cells, output_dir="debug_cells"):
    """Saves individual processed cells to disk and plots the 9x9 grid window."""
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(9, 9, figsize=(9, 9))
    fig.suptitle("Final Cleaned Cells Preview", fontsize=14)
    
    for idx, cell in enumerate(cells):
        row, col = divmod(idx, 9)
        
        cell_filename = os.path.join(output_dir, f"cell_{row}_{col}.png")
        cv2.imwrite(cell_filename, cell)
        
        ax = axes[row, col]
        ax.imshow(cell, cmap='gray', vmin=0, vmax=255)
        ax.axis('off')
        
    plt.tight_layout()
    plt.show()

def classify_image(image_path, debug=True):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"The image file {image_path} could not be found or opened.")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    processed = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    grid_size = 288
    resized = cv2.resize(processed, (grid_size, grid_size))
    
    cell_size = grid_size // 9
    cells = []
    board_matrix = np.zeros((9, 9), dtype=int)
    
    for i in range(9):
        for j in range(9):
            y1, y2 = i * cell_size, (i + 1) * cell_size
            x1, x2 = j * cell_size, (j + 1) * cell_size
            raw_cell = resized[y1:y2, x1:x2]
            
            # Gentle 3% margin trim to clear grid borders without clipping text
            mh, mw = raw_cell.shape
            pad_y, pad_x = int(mh * 0.03), int(mw * 0.03)
            trimmed_cell = raw_cell[pad_y:mh-pad_y, pad_x:mw-pad_x]
            
            # Process cell (removes grid lines, centers digit on 32x32 canvas)
            processed_cell = process_cell(trimmed_cell)
            cells.append(processed_cell)
            
            # Check if cell is blank using pixel brightness and contour area
            inv_cell = cv2.bitwise_not(processed_cell)
            contours, _ = cv2.findContours(inv_cell, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            has_valid_digit = False
            if contours:
                max_area = max(cv2.contourArea(c) for c in contours)
                if max_area > 40:  # Minimum pixel area for a valid digit stroke
                    has_valid_digit = True

            if not has_valid_digit or np.mean(processed_cell) > 253:
                board_matrix[i, j] = 0
            else:
                board_matrix[i, j] = classify_cell(processed_cell)
            
    if debug:
        save_and_display_cells(cells)
        
    return board_matrix

if __name__ == "__main__":
    image_path = "sudoku_test.png"
    board_grid = classify_image(image_path, debug=True)
    print("Extracted Sudoku Board Matrix:")
    print(board_grid)