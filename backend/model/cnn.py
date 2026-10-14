import torch
import torch.nn as nn
import torch.nn.functional as F

class SudokuCNN(nn.Module):
    def __init__(self):
        super(SudokuCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)
        self.fc1 = nn.Linear(64 * 8 * 8, 128)  # Corrected size
        self.fc2 = nn.Linear(128, 10)  # Corrected size

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 8 * 8)  # Flatten
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x
    
    def load_weights(self, weight_path, device="cpu"):
        """Loads trained weights into the model state dictionary."""
        self.load_state_dict(torch.load(weight_path, map_location=device))
        self.eval()