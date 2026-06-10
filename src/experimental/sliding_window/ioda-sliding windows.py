#!/usr/bin/env python
# coding: utf-8

# In[4]:


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

# Sigmoid for VFBLS
def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

# ReLU for BLS
def relu(x):
    return np.maximum(x, 0)

datasets = {
    'Zhytomyr': 'ioda_region_4369_zhytomyr.csv',
    'Iraq': 'ioda_country_IQ_iraq.csv',
    'Gaza': 'ioda_region_1226_gazastrip.csv'
}

# PyTorch Models
class LSTMModel(nn.Module):
    def __init__(self, d, seq_len):
        super().__init__()
        self.lstm = nn.LSTM(d, 64, batch_first=True)
        self.fc = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1), nn.Sigmoid())
    def forward(self, x):
        _, (h, _) = self.lstm(x)
        return self.fc(h.squeeze(0)).view(-1)

class BiLSTMModel(nn.Module):
    def __init__(self, d, seq_len, h=64, drop=0.3):
        super().__init__()
        self.lstm = nn.LSTM(d, h, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(nn.Linear(h*2, 64), nn.ReLU(), nn.Dropout(drop), nn.Linear(64, 1), nn.Sigmoid())
    def forward(self, x):
        _, (h, _) = self.lstm(x)
        h = torch.cat((h[0], h[1]), dim=1)
        return self.fc(h).view(-1)

class GRUModel(nn.Module):
    def __init__(self, d, seq_len):
        super().__init__()
        self.gru = nn.GRU(d, 64, batch_first=True)
        self.fc = nn.Sequential(nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1), nn.Sigmoid())
    def forward(self, x):
        _, h = self.gru(x)
        return self.fc(h.squeeze(0)).view(-1)

class BiGRUModel(nn.Module):
    def __init__(self, d, seq_len, h=64, drop=0.3):
        super().__init__()
        self.gru = nn.GRU(d, h, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(nn.Linear(h*2, 64), nn.ReLU(), nn.Dropout(drop), nn.Linear(64, 1), nn.Sigmoid())
    def forward(self, x):
        _, h = self.gru(x)
        h = torch.cat((h[0], h[1]), dim=1)
        return self.fc(h).view(-1)

class CNN1DModel(nn.Module):
    def __init__(self, d, seq_len):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(d, 64, 3, padding=1), nn.ReLU(),
            nn.Conv1d(64, 32, 3, padding=1), nn.ReLU(),
            nn.AdaptiveMaxPool1d(1), nn.Flatten(),
            nn.Linear(32, 1), nn.Sigmoid()
        )
    def forward(self, x):
        x = x.permute(0, 2, 1)  # [batch, features, seq_len] for Conv1d
        return self.net(x).view(-1)

# VFBLS
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

# BLS (basic version with ReLU for enhancement)
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

# Manual imputation (median per column)
def manual_impute_median(X):
    for j in range(X.shape[1]):
        col = X[:, j]
        non_nan = col[~np.isnan(col)]
        if len(non_nan) > 0:
            med = np.median(non_nan)
            col[np.isnan(col)] = med
    return X

# Manual scaling (z-score per column)
def manual_scale(X):
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)
    std[std == 0] = 1  # Avoid division by zero
    return (X - mean) / std

# Manual stratified train_test_split
def manual_stratified_split(X, y, test_size=0.3, random_state=42):
    np.random.seed(random_state)
    idx0 = np.where(y == 0)[0]
    idx1 = np.where(y == 1)[0]
    n_test0 = int(len(idx0) * test_size)
    n_test1 = int(len(idx1) * test_size)
    test_idx0 = np.random.choice(idx0, n_test0, replace=False)
    test_idx1 = np.random.choice(idx1, n_test1, replace=False)
    test_idx = np.concatenate([test_idx0, test_idx1])
    train_idx = np.setdiff1d(np.arange(len(y)), test_idx)
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]

# Manual confusion matrix
def manual_confusion_matrix(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    return tp, fp, fn, tn

# Manual ROC AUC
def manual_roc_auc_score(y_true, y_score):
    idx = np.argsort(y_score)[::-1]
    y_true = y_true[idx]
    y_score = y_score[idx]
    tpr = np.cumsum(y_true) / np.sum(y_true) if np.sum(y_true) > 0 else np.zeros(len(y_true))
    fpr = np.cumsum(1 - y_true) / np.sum(1 - y_true) if np.sum(1 - y_true) > 0 else np.zeros(len(y_true))
    return np.trapezoid(tpr, fpr)

# Manual precision_recall_curve
def manual_precision_recall_curve(y_true, y_score):
    if len(y_true) == 0:
        return np.array([1.0]), np.array([0.0]), np.array([])
    idx = np.argsort(y_score)[::-1]
    y_true = y_true[idx]
    y_score = y_score[idx]
    distinct_value_indices = np.where(np.diff(y_score) != 0)[0]
    threshold_idxs = np.r_[distinct_value_indices, y_true.size - 1]
    tps = np.cumsum(y_true)[threshold_idxs]
    fps = np.cumsum(1 - y_true)[threshold_idxs]
    thresholds = y_score[threshold_idxs]
    with np.errstate(divide='ignore', invalid='ignore'):
        prec = tps / (tps + fps)
    prec[np.isnan(prec)] = 0.0
    rec = tps / np.sum(y_true) if np.sum(y_true) > 0 else np.zeros_like(tps)
    return prec, rec, thresholds

# Manual average_precision_score
def manual_average_precision_score(y_true, y_score):
    prec, rec, _ = manual_precision_recall_curve(y_true, y_score)
    if len(rec) == 0:
        return 0.0
    return np.sum(np.diff(rec) * prec[:-1])

def evaluate(p, y):
    p = np.clip(p, 1e-8, 1-1e-8)
    if np.sum(y) == 0 or np.sum(y == 0) == 0:
        return {'ROC-AUC':'N/A','PR-AUC':'N/A','Accuracy':'0.000000','F1-Score':'0.000000',
                'TP':0,'FP':0,'FN':0,'TN':0,'Threshold':'0.500000','Precision':'0.000000','Sensitivity':'0.000000'}
    prec, rec, thr = manual_precision_recall_curve(y, p)
    f1 = 2 * prec * rec / (prec + rec + 1e-12)
    idx = np.argmax(f1)
    thr_val = thr[idx] if len(thr) > idx else 0.5
    pred = (p >= thr_val).astype(int)
    f1_val = f1[idx]
    tp, fp, fn, tn = manual_confusion_matrix(y, pred)
    accuracy = (tp + tn) / len(y)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    roc_auc = manual_roc_auc_score(y, p)
    pr_auc = manual_average_precision_score(y, p)
    return {
        'ROC-AUC': f'{roc_auc:.4f}',
        'PR-AUC': f'{pr_auc:.4f}',
        'Accuracy': f'{accuracy:.6f}',
        'F1-Score': f'{f1_val:.6f}',
        'TP': int(tp), 'FP': int(fp), 'FN': int(fn), 'TN': int(tn),
        'Threshold': f'{thr_val:.6f}',
        'Precision': f'{precision:.6f}',
        'Sensitivity': f'{sensitivity:.6f}'
    }

def create_sliding_windows(X, y, window_size):
    X_windows = []
    y_windows = []
    for i in range(len(X) - window_size + 1):
        X_windows.append(X[i:i + window_size])
        y_windows.append(y[i + window_size - 1])
    return np.array(X_windows), np.array(y_windows)

# Main
window_size = 10  # Configurable, as per paper tested 1-300
print("IODA Anomaly Detection with Sliding Windows – CNN, RNN-GRU, LSTM, Bi-GRU, Bi-LSTM, BLS, VFBLS, GBDT-LightGBM")
print("="*90)
for ds_name, path in datasets.items():
    if not os.path.exists(path):
        print(f"{path} not found → skipping {ds_name}")
        continue
    print(f"\n=== {ds_name.upper()} (Window Size: {window_size}) ===")
    df = pd.read_csv(path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime')  # Ensure chronological order
    df['LABEL'] = 0
    if ds_name == 'Zhytomyr':
        start = pd.to_datetime('2022-03-21 12:00:00+00:00')
        end = pd.to_datetime('2022-03-22 12:00:00+00:00')
        df.loc[(df['datetime'] >= start) & (df['datetime'] <= end), 'LABEL'] = 1
    elif ds_name == 'Iraq':
        for day in range(21, 31):
            start = pd.to_datetime(f'2023-08-{day:02d} 01:00:00+00:00')
            end = pd.to_datetime(f'2023-08-{day:02d} 05:00:00+00:00')
            df.loc[(df['datetime'] >= start) & (df['datetime'] <= end), 'LABEL'] = 1
    elif ds_name == 'Gaza':
        start = pd.to_datetime('2023-10-27 16:00:00+00:00')
        end = pd.to_datetime('2023-10-29 03:00:00+00:00')
        df.loc[(df['datetime'] >= start) & (df['datetime'] <= end), 'LABEL'] = 1
    y = df['LABEL'].values.astype(int)
    if ds_name == 'Iraq':
        cols = ['merit-nt', 'bgp', 'ping-slash24', 'gtr-norm']
    else:
        cols = ['merit-nt', 'bgp', 'ping-slash24']
    X = df[cols].values.astype(np.float32)
    print(f"Original Samples: {len(y):,} | Anomalies: {y.sum():,} ({y.mean()*100:.3f}%)")
    X = manual_impute_median(X)
    X = manual_scale(X)
    # Feature selection before windows
    if len(cols) > 1:
        selector = ExtraTreesClassifier(n_estimators=50)
        selector.fit(X, y)
        sfm = SelectFromModel(selector, prefit=True)
        X = sfm.transform(X)
        num_selected = X.shape[1]
        print(f"Selected {num_selected} features")
    X_seq, y_seq = create_sliding_windows(X, y, window_size)
    print(f"After Windows: {len(y_seq):,} samples")
    X_tr, X_te, y_tr, y_te = manual_stratified_split(X_seq, y_seq)
    tr_tensor = torch.FloatTensor(X_tr)  # [batch, seq, features]
    te_tensor = torch.FloatTensor(X_te)
    loader = DataLoader(TensorDataset(tr_tensor, torch.FloatTensor(y_tr)), batch_size=64, shuffle=True)
    results = {}
    times = {}
    # GBDT-LightGBM (flatten for non-seq model)
    X_tr_flat = X_tr.reshape(X_tr.shape[0], -1)
    X_te_flat = X_te.reshape(X_te.shape[0], -1)
    t0 = time.time()
    gbm = lgb.train({'objective':'binary','verbose':-1}, lgb.Dataset(X_tr_flat, y_tr), num_boost_round=300)
    results['GBDT-LightGBM'] = gbm.predict(X_te_flat)
    times['GBDT-LightGBM'] = time.time() - t0
    # Torch models in order
    for name, cls, epochs in [
        ('CNN', CNN1DModel, 12),
        ('RNN-GRU', GRUModel, 12),
        ('LSTM', LSTMModel, 12),
        ('Bi-GRU', BiGRUModel, 15),
        ('Bi-LSTM', BiLSTMModel, 15)
    ]:
        t0 = time.time()
        model = cls(X_tr.shape[2], window_size)
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
    print("Model           ROC-AUC PR-AUC Accuracy F1-Score TP  FP  FN   TN   Threshold Precision Sensitivity")
    print("-"*100)
    for m in model_order:
        if m in results:
            e = evaluate(results[m], y_te)
            print(f"{m:<15} {e['ROC-AUC']}  {e['PR-AUC']} {e['Accuracy']} {e['F1-Score']} {e['TP']:>3} {e['FP']:>3} {e['FN']:>3} {e['TN']:>4} {e['Threshold']} {e['Precision']} {e['Sensitivity']}")
    print("\nTraining time (seconds):")
    for m in model_order:
        if m in times:
            print(f" {m:<15} {times[m]:.3f}s")
    print("\n" + "="*90)
print("Finished. Usual winners: Bi-GRU ≈ Bi-LSTM > CNN > others | Fastest: VFBLS / BLS")


# In[ ]:




