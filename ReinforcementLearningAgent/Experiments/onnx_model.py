import time
import torch
import torch.nn as nn
import onnxruntime as ort
import numpy as np


# Example: Residual block
class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)

    def forward(self, x):
        return self.relu(x + self.conv2(self.relu(self.conv1(x))))


# Residual tower with 10 blocks
class ResTower(nn.Module):
    def __init__(self, channels=64):
        super().__init__()
        self.blocks = nn.Sequential(*[ResidualBlock(channels) for _ in range(10)])

    def forward(self, x):
        return self.blocks(x)


model = ResTower().eval()

# Dummy input
inp = torch.randn(1, 64, 64, 64)

# Export to ONNX
torch.onnx.export(model, inp, "restower.onnx", opset_version=17)

# PyTorch timing
with torch.no_grad():
    for _ in range(5):
        model(inp)  # warmup
    start = time.time()
    for _ in range(100):
        model(inp)
    print("PyTorch time:", time.time() - start)

# ONNX Runtime timing
ort_session = ort.InferenceSession("restower.onnx", providers=["CPUExecutionProvider"])
input_data = inp.numpy()
for _ in range(5):
    ort_session.run(None, {"input.1": input_data})  # warmup
start = time.time()
for _ in range(100):
    ort_session.run(None, {"input.1": input_data})
print("ONNX Runtime time:", time.time() - start)
