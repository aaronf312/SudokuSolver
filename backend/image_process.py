import cv2 
import numpy as np
from rapidocr_onnxruntime import RapidOCR

ocr_engine = RapidOCR()

#This file is designed to take in an image and return a readable sudoku puzzle
#Typical ocr does not like reading from the entire sudoku grid, will need to pass in one cell at a time

#Grayscaling

#Binarization

#Noise Reduction

#Deskew

#Borders

def extract_text(image_path: str):
    #Reading from react
    #nparr = np.frombuffer(image_bytes,np.uint8)
    #img = cv2.imdecode(nparr,cv2.IMREAD_COLOR)

    #Preprocess

    img = cv2.imread(image_path)

    result, elapse = ocr_engine(img)

    if result:
        for box, text, score in result:
            print(f"Detected: '{text}' (Confidence: {float(score):.2f})")
    else:
        print("No text detected.")

if __name__ == "__main__":
    extract_text("words_test.png")