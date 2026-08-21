import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import os

class ToyNet(nn.Module):
    def __init__(self):
        super(ToyNet, self).__init__()
        # Small fully-connected network <10k params
        self.fc1 = nn.Linear(2, 32)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(32, 16)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(16, 2)
        
    def forward(self, x):
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x

def create_toy_data():
    # Synthetic 2D classification problem
    torch.manual_seed(42)
    X = torch.rand(1000, 2) * 2 - 1 # range [-1, 1]
    # Label 1 if inside unit circle, else 0
    Y = (X[:, 0]**2 + X[:, 1]**2 < 0.5).long()
    return X, Y

def main():
    print("Setting up training data...")
    X, Y = create_toy_data()
    dataset = TensorDataset(X, Y)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    model = ToyNet()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    epochs = 10
    print("Starting training...")
    for epoch in range(epochs):
        total_loss = 0
        for batch_X, batch_Y in dataloader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_Y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(dataloader):.4f}")
        
    # Save the model
    os.makedirs("models", exist_ok=True)
    model_path = os.path.join("models", "toy_model.pt")
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    main()
