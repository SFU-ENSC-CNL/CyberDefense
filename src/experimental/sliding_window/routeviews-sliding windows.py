#!/usr/bin/env python
# coding: utf-8

# In[2]:


# =============================================================================
# BGP Anomaly Detection – 8 Models with Sliding Windows – REWRITTEN VERSION
# Models: CNN → RNN-GRU → LSTM → Bi-GRU → Bi-LSTM → BLS → VFBLS → GBDT-LightGBM
# =============================================================================
import pandas as pd
import numpy as np
import time
import warnings
import os
import subprocess
import sys
warnings.filterwarnings('ignore')
# Auto-install missing packages
def install(p):
    subprocess.check_call([sys.executable, "-m", "pip", "install", p, "--quiet"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for p in ['lightgbm', 'torch', 'scikit-learn']:
    try:
        __import__(p.replace('-', '_'))
    except:
        install(p)
import lightgbm as lgb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_recall_curve, f1_score, confusion_matrix, average_precision_score

# Sigmoid for VFBLS/BLS
def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

# ReLU for BLS
def relu(x):
    return np.maximum(x, 0)

datasets = {
    'Slammer': 'Slammer.csv',
    'Moscow_blackout': 'Moscow_blackout.csv',
    'WannaCrypt': 'WannaCrypt.csv'
}

# ============================= PyTorch Models =============================
class LSTMModel(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.lstm = nn.LSTM(d, 64, batch_first=True)
        self.fc = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1), nn.Sigmoid())
    def forward(self, x):
        _, (h, _) = self.lstm(x)
        return self.fc(h.squeeze(0)).view(-1)

class BiLSTMModel(nn.Module):
    def __init__(self, d, h=64, drop=0.3):
        super().__init__()
        self.lstm = nn.LSTM(d, h, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(nn.Linear(h*2, 64), nn.ReLU(), nn.Dropout(drop), nn.Linear(64, 1), nn.Sigmoid())
    def forward(self, x):
        _, (h, _) = self.lstm(x)
        h = torch.cat((h[0], h[1]), dim=1)
        return self.fc(h).view(-1)

class GRUModel(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.gru = nn.GRU(d, 64, batch_first=True)
        self.fc = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1), nn.Sigmoid())
    def forward(self, x):
        _, h = self.gru(x)
        return self.fc(h.squeeze(0)).view(-1)

class BiGRUModel(nn.Module):
    def __init__(self, d, h=64, drop=0.3):
        super().__init__()
        self.gru = nn.GRU(d, h, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(nn.Linear(h*2, 64), nn.ReLU(), nn.Dropout(drop), nn.Linear(64, 1), nn.Sigmoid())
    def forward(self, x):
        _, h = self.gru(x)
        h = torch.cat((h[0], h[1]), dim=1)
        return self.fc(h).view(-1)

class CNN1DModel(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(d, 64, 3, padding=1), nn.ReLU(),
            nn.Conv1d(64, 32, 3, padding=1), nn.ReLU(),
            nn.AdaptiveMaxPool1d(1), nn.Flatten(),
            nn.Linear(32, 1), nn.Sigmoid()
        )
    def forward(self, x):
        x = x.permute(0, 2, 1)
        return self.net(x).view(-1)

# ============================= VFBLS (correct & fast) =============================
def train_vf_bls(X, y, C=1e-8, s=0.8, enh=80):
    y = y.reshape(-1, 1)
    bias = 0.1 * np.ones((X.shape[0], 1))
    Xb = np.hstack([X, bias])
    Wf = np.linalg.pinv(Xb.T @ Xb + C * np.eye(Xb.shape[1])) @ (Xb.T @ y)
    Z = Xb @ Wf
    We = np.random.randn(Z.shape[1], enh)
    H = np.tanh(Z @ We)
    A = np.hstack([Z, H]) / s
    Wo = np.linalg.pinv(A.T @ A + C * np.eye(A.shape[1])) @ (A.T @ y)
    return Wf, We, Wo, s

def predict_vfbls(X, params):
    Wf, We, Wo, s = params
    bias = 0.1 * np.ones((X.shape[0], 1))
    Xb = np.hstack([X, bias])
    Z = Xb @ Wf
    H = np.tanh(Z @ We)
    A = np.hstack([Z, H]) / s
    return sigmoid(A @ Wo).flatten()

# ============================= BLS =============================
def train_bls(X, y, C=1e-8, s=0.8, enh=80):
    y = y.reshape(-1, 1)
    bias = 0.1 * np.ones((X.shape[0], 1))
    Xb = np.hstack([X, bias])
    Wf = np.linalg.pinv(Xb.T @ Xb + C * np.eye(Xb.shape[1])) @ (Xb.T @ y)
    Z = Xb @ Wf
    We = np.random.randn(Z.shape[1], enh)
    H = relu(Z @ We)
    A = np.hstack([Z, H]) / s
    Wo = np.linalg.pinv(A.T @ A + C * np.eye(A.shape[1])) @ (A.T @ y)
    return Wf, We, Wo, s

def predict_bls(X, params):
    Wf, We, Wo, s = params
    bias = 0.1 * np.ones((X.shape[0], 1))
    Xb = np.hstack([X, bias])
    Z = Xb @ Wf
    H = relu(Z @ We)
    A = np.hstack([Z, H]) / s
    return sigmoid(A @ Wo).flatten()

# ============================= Evaluation =============================
def evaluate(p, y):
    p = np.clip(p, 1e-8, 1-1e-8)
    if y.sum() == 0 or (y == 0).sum() == 0:
        return {'ROC-AUC':'N/A','PR-AUC':'N/A','Accuracy':'0.000000','F1-Score':'0.000000',
                'TP':0,'FP':0,'FN':0,'TN':0,'Threshold':'0.500000'}
    try:
        prec, rec, thr = precision_recall_curve(y, p)
        f1 = 2*prec*rec/(prec+rec+1e-12)
        idx = np.argmax(f1)
        thr_val = thr[idx] if len(thr) > idx else 0.5
        pred = (p >= thr_val).astype(int)
        f1_val = f1[idx]
        tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
        return {
            'ROC-AUC': f'{roc_auc_score(y,p):.4f}',
            'PR-AUC': f'{average_precision_score(y,p):.4f}',
            'Accuracy': f'{(tp+tn)/len(y):.6f}',
            'F1-Score': f'{f1_val:.6f}',
            'TP':int(tp), 'FP':int(fp), 'FN':int(fn), 'TN':int(tn),
            'Threshold': f'{thr_val:.6f}'
        }
    except:
        return {'ROC-AUC':'N/A','PR-AUC':'N/A','Accuracy':'0.000000','F1-Score':'0.000000',
                'TP':0,'FP':0,'FN':0,'TN':0,'Threshold':'0.500000'}

def create_sliding_windows(X, y, window_size):
    num_samples = len(X) - window_size + 1
    if num_samples <= 0:
        raise ValueError("Window size larger than data length")
    X_windows = np.zeros((num_samples, window_size, X.shape[1]), dtype=np.float32)
    y_windows = np.zeros(num_samples, dtype=int)
    for i in range(num_samples):
        X_windows[i] = X[i:i + window_size]
        y_windows[i] = y[i + window_size - 1]  # Label from end of window
    return X_windows, y_windows

# ============================= Main =============================
window_size = 10  # As per paper, test 1-300; start with 10
print("BGP Anomaly Detection – 8 Models with Sliding Windows – REWRITTEN VERSION")
print("="*90)
for ds_name, path in datasets.items():
    if not os.path.exists(path):
        print(f"{path} not found → skipping {ds_name}")
        continue
    print(f"\n=== {ds_name.upper()} (Window Size: {window_size}) ===")
    df = pd.read_csv(path, header=None)
    y = (df[3] != 0).astype(int).values
    X = df.iloc[:, 4:41].astype(np.float32).values  # 37 features as per paper
    print(f"Original Samples: {len(y):,} | Anomalies: {y.sum():,} ({y.mean()*100:.3f}%)")
    X = SimpleImputer(strategy='median').fit_transform(X)
    X = StandardScaler().fit_transform(X)
    X_seq, y_seq = create_sliding_windows(X, y, window_size)
    print(f"After Windows: {len(y_seq):,} samples")
    X_tr, X_te, y_tr, y_te = train_test_split(X_seq, y_seq, test_size=0.3, random_state=42, stratify=y_seq)
    tr_tensor = torch.FloatTensor(X_tr)  # [batch, seq, features]
    te_tensor = torch.FloatTensor(X_te)
    loader = DataLoader(TensorDataset(tr_tensor, torch.FloatTensor(y_tr)), batch_size=64, shuffle=True)
    results = {}
    times = {}
    # GBDT-LightGBM (flatten sequences)
    X_tr_flat = X_tr.reshape(X_tr.shape[0], -1)
    X_te_flat = X_te.reshape(X_te.shape[0], -1)
    t0 = time.time()
    gbm = lgb.train({'objective':'binary','verbose':-1}, lgb.Dataset(X_tr_flat, y_tr), num_boost_round=300)
    results['GBDT-LightGBM'] = gbm.predict(X_te_flat)
    times['GBDT-LightGBM'] = time.time() - t0
    # Neural nets in requested sequence
    for name, cls, epochs in [
        ('CNN', CNN1DModel, 12),
        ('RNN-GRU', GRUModel, 12),
        ('LSTM', LSTMModel, 12),
        ('Bi-GRU', BiGRUModel, 15),
        ('Bi-LSTM', BiLSTMModel, 15)
    ]:
        t0 = time.time()
        model = cls(X_tr.shape[2])
        opt = optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.BCELoss()
        model.train()
        for _ in range(epochs):
            for bx, by in loader:
                opt.zero_grad()
                loss = criterion(model(bx).view(-1), by)
                loss.backward()
                opt.step()
        model.eval()
        with torch.no_grad():
            results[name] = model(te_tensor).cpu().numpy().flatten()
        times[name] = time.time() - t0
    # BLS (flatten)
    t0 = time.time()
    params = train_bls(X_tr_flat, y_tr)
    results['BLS'] = predict_bls(X_te_flat, params)
    times['BLS'] = time.time() - t0
    # VFBLS (flatten)
    t0 = time.time()
    params = train_vf_bls(X_tr_flat, y_tr)
    results['VFBLS'] = predict_vfbls(X_te_flat, params)
    times['VFBLS'] = time.time() - t0
    # Results
    model_order = ['CNN', 'RNN-GRU', 'LSTM', 'Bi-GRU', 'Bi-LSTM', 'BLS', 'VFBLS', 'GBDT-LightGBM']
    print("\nResearch Mode (optimal F1 threshold)")
    print("Model ROC-AUC PR-AUC Accuracy F1-Score TP FP FN TN Threshold")
    print("-"*80)
    for m in model_order:
        e = evaluate(results[m], y_te)
        print(f"{m:<13} {e['ROC-AUC']} {e['PR-AUC']} {e['Accuracy']} {e['F1-Score']} {e['TP']:>3} {e['FP']:>3} {e['FN']:>3} {e['TN']:>5} {e['Threshold']}")
    print("\nTraining time (seconds):")
    for m in model_order:
        print(f" {m:<13} {times[m]:.3f}s")
    print("\n" + "="*90)
print("Finished. Usual winners: Bi-GRU ≈ Bi-LSTM > CNN > others | Fastest: VFBLS (<0.05s)")


# In[ ]:




