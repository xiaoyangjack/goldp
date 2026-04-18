import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class IVSurfaceModel(nn.Module):
    def __init__(self, input_dim=3, hidden_dim=128, output_dim=1):
        super(IVSurfaceModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        return self.network(x)

class IVSurfaceFitter:
    def __init__(self):
        self.model = IVSurfaceModel()
        self.scaler = StandardScaler()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
    
    def prepare_data(self, option_data):
        X = []
        y = []
        
        for _, row in option_data.iterrows():
            # 输入特征：moneyness, time_to_expiry, implied_volatility
            moneyness = row['strike'] / row['underlying_price']
            time_to_expiry = row['time_to_expiry'] / 365.0  # 转换为年
            iv = row['implied_volatility']
            
            X.append([moneyness, time_to_expiry, row['underlying_price']])
            y.append(iv)
        
        X = np.array(X)
        y = np.array(y)
        
        # 数据标准化
        X_scaled = self.scaler.fit_transform(X)
        
        return train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    
    def train(self, X_train, y_train, epochs=100):
        self.model.train()
        
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            
            X_tensor = torch.tensor(X_train, dtype=torch.float32)
            y_tensor = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
            
            predictions = self.model(X_tensor)
            loss = self.criterion(predictions, y_tensor)
            
            loss.backward()
            self.optimizer.step()
            
            if epoch % 10 == 0:
                print(f'Epoch {epoch}, Loss: {loss.item():.4f}')
    
    def predict_iv(self, moneyness, time_to_expiry, underlying_price):
        self.model.eval()
        
        input_data = np.array([[moneyness, time_to_expiry / 365.0, underlying_price]])
        input_scaled = self.scaler.transform(input_data)
        
        with torch.no_grad():
            prediction = self.model(torch.tensor(input_scaled, dtype=torch.float32))
        
        return prediction.item()
    
    def fit_surface(self, option_data):
        X_train, X_test, y_train, y_test = self.prepare_data(option_data)
        self.train(X_train, y_train)
        
        # 评估模型
        self.model.eval()
        with torch.no_grad():
            X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
            y_test_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)
            test_predictions = self.model(X_test_tensor)
            test_loss = self.criterion(test_predictions, y_test_tensor)
        
        print(f'Test Loss: {test_loss.item():.4f}')
        return self