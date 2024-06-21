import torch
import torch.nn as nn
import torch.nn.functional as F

class Actor(nn.Module):
    def __init__(self, init_w=3e-3):
        super(Actor, self).__init__()
        self.conv1 = nn.Conv2d(12, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(32, 4, kernel_size=3, padding=1)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(4 * 16 * 24, 64)
        self.fc2 = nn.Linear(64, 4)

    def forward(self, x):
        out = F.max_pool2d(torch.relu(self.conv1(x)), 2)
        out = F.max_pool2d(torch.relu(self.conv2(out)), 2)
        out = F.max_pool2d(torch.relu(self.conv3(out)), 2)
        out = self.flatten(out)
        out = torch.relu(self.fc1(out))
        out = torch.tanh(self.fc2(out))
        return out

class Critic(nn.Module):
    def __init__(self, init_w=3e-3):
        super(Critic, self).__init__()
        self.conv1 = nn.Conv2d(12, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(32, 4, kernel_size=3, padding=1)
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(4 * 16 * 24 + 4, 64)
        self.fc2 = nn.Linear(64, 1)

    def forward(self, xs):
        x, a = xs
        out = F.max_pool2d(torch.relu(self.conv1(x)), 2)
        out = F.max_pool2d(torch.relu(self.conv2(out)), 2)
        out = F.max_pool2d(torch.relu(self.conv3(out)), 2)
        out = self.flatten(out)
        out = torch.cat([out, a], 1)
        out = torch.relu(self.fc1(out))
        out = torch.tanh(self.fc2(out))
        return out
