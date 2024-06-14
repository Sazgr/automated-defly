import torch
import torch.nn as nn

model = nn.Sequential(
    nn.Conv2d(12, 32, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(32, 32, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Conv2d(32, 4, kernel_size=3, padding=1),
    nn.ReLU(),
    nn.MaxPool2d(2),
    nn.Flatten(),
    nn.Linear(4 * 16 * 16, 64),
    nn.ReLU(), 
    nn.Linear(64, 4)
    nn.Tanh()
)
