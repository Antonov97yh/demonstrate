import torch
import joblib
import numpy as np
import pandas as pd
from torch import nn
import torch.nn.functional as F

# 1. Определите архитектуру модели (как при обучении)
class FeatureAttention(nn.Module):
    def __init__(self, input_dim, units):
        super(FeatureAttention, self).__init__()
        self.units = units
        self.query = nn.Linear(input_dim, units)
        self.key = nn.Linear(input_dim, units)
        self.value = nn.Linear(input_dim, units)
        self.attention_weights = None

    def forward(self, x):
        Q = self.query(x)
        K = self.key(x)
        V = self.value(x)

        attention_scores = torch.matmul(Q, K.transpose(-2, -1)) / torch.sqrt(torch.tensor(self.units, dtype=torch.float32))
        self.attention_weights = F.softmax(attention_scores, dim=-1)
        output = torch.matmul(self.attention_weights, V)
        return output

class FiNetWithAttention(nn.Module):
    def __init__(self, input_dim, num_blocks=3, hidden_units=64, dropout_rate=0.2):
        super(FiNetWithAttention, self).__init__()
        self.input_dim = input_dim
        self.num_blocks = num_blocks
        self.hidden_units = hidden_units

        self.embedding = nn.Sequential(
            nn.Linear(input_dim, hidden_units),
            nn.ReLU(),
            nn.LayerNorm(hidden_units)
        )

        self.blocks = nn.ModuleList()
        for _ in range(num_blocks):
            block = nn.ModuleDict({
                'attention': FeatureAttention(hidden_units, hidden_units),
                'dense1': nn.Linear(hidden_units, hidden_units),
                'dense2': nn.Linear(hidden_units, hidden_units),
                'ln': nn.LayerNorm(hidden_units),
                'dropout': nn.Dropout(dropout_rate)
            })
            self.blocks.append(block)

        self.output_layer = nn.Sequential(
            nn.Linear(hidden_units, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.embedding(x)

        for block in self.blocks:
            attn_out = block['attention'](x)
            attn_out = block['dense1'](attn_out)
            attn_out = F.relu(attn_out)

            x_interaction = x * attn_out
            x_interaction = block['dense2'](x_interaction)
            x_interaction = F.relu(x_interaction)

            x = x + x_interaction
            x = block['ln'](x)
            x = block['dropout'](x)

        return self.output_layer(x)

    def get_attention_weights(self):
        """Возвращает веса внимания из всех блоков"""
        return [block['attention'].attention_weights for block in self.blocks]


INPUT_DIM = 19  # Замените на реальное количество фичей

# Загрузка модели и scaler
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = FiNetWithAttention(INPUT_DIM).to(device)
model.load_state_dict(torch.load('mortgage_model.pth', map_location=device))  # Замените на свой путь
model.eval()  # Переводим модель в режим предсказания

scaler = joblib.load('mortgage_scaler.pkl')  # Замените на свой путь

# 2. Загрузка модели и scaler
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = FiNetWithAttention(INPUT_DIM).to(device)
model.load_state_dict(torch.load('mortgage_model.pth', map_location=device))
model.eval()

scaler = joblib.load('mortgage_scaler.pkl')

# 3. Загрузка новых данных
new_data = pd.read_csv('new_data.csv')  # Замените на свои данные
X_scaled = scaler.transform(new_data)
X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(device)

# 4. Предсказание
with torch.no_grad():
    predictions = model(X_tensor).cpu().numpy()

print("Результаты предсказания:", predictions)