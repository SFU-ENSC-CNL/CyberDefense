import numpy as np
import torch
from torch import nn
import torch.utils.data as Data
import torch.nn.functional as F
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score

class StatsCollector():
    def __init__(self):
        self.data = {}

    def collect(self, key, value):
        self.data[key] = value

class Loader():
    def __init__(self, fname, batch_size=128, shuffle=False):
        self.fname = fname
        self.batch_size = batch_size
        self.shuffle = shuffle

        train = np.loadtxt(fname, delimiter=",")
        _,sz = train.shape
        xs = train[:,0:sz-1]
        ys = train[:,sz-1]
        torch_xs = torch.from_numpy(xs)
        torch_ys = torch.from_numpy(ys)
        torch_xs = torch_xs.to(torch.float)
        torch_ys = torch_ys.to(torch.long)
        torch_data = Data.TensorDataset(torch_xs, torch_ys)

        self.xs = torch_xs
        self.ys = torch_ys
        self.data_loader = Data.DataLoader(dataset=torch_data, batch_size=self.batch_size, shuffle=self.shuffle)

class RNN_GRU(nn.Module):

    def __init__(self, hidden_sizes=[128], num_layers=2, num_classes=2, input_sz=128, batch_first=False, dropout=0.4):
        super(RNN_GRU, self).__init__()
        self.hidden_sizes = hidden_sizes
        self.hidden_layers = nn.ModuleList()
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.input_lstm = input_sz
        self.batch_first = batch_first
        self.dropout = dropout

        self.gru = nn.GRU(input_sz, self.hidden_sizes[0], self.num_layers, batch_first=self.batch_first, dropout=self.dropout)
        self.relu = nn.ReLU()
        self.keke_drop = nn.Dropout(p=0.5)

        if len(self.hidden_sizes) == 3:
            # Reproduces a construction-order bug in the original gru_4layer.py
            # template: it built fc4 (hidden_sizes[2] -> num_classes) *before*
            # fc35 (hidden_sizes[1] -> hidden_sizes[2]). Since nn.Linear draws its
            # initial weights from the shared global RNG at construction time,
            # that swap changes every weight in the model relative to building
            # the layers in logical order, even though shapes are identical.
            # Build in the buggy order, but store in the correct forward-pass order.
            fc3 = nn.Linear(self.hidden_sizes[0], self.hidden_sizes[1])
            fc4 = nn.Linear(self.hidden_sizes[2], self.num_classes)
            fc35 = nn.Linear(self.hidden_sizes[1], self.hidden_sizes[2])
            self.hidden_layers.append(fc3)
            self.hidden_layers.append(fc35)
            self.hidden_layers.append(fc4)
        else:
            for k in range(len(self.hidden_sizes)):
                if k < len(self.hidden_sizes)-1:
                    self.hidden_layers.append(nn.Linear(self.hidden_sizes[k], self.hidden_sizes[k+1]))
                else:
                    self.hidden_layers.append(nn.Linear(self.hidden_sizes[k], self.num_classes))

    def forward(self, x):
        if torch.cuda.is_available():
            h0 = torch.zeros(self.num_layers, x.size(1), self.hidden_sizes[0]).cuda()
        else:
            h0 = torch.zeros(self.num_layers, x.size(1), self.hidden_sizes[0])

        x, _ = self.gru(x, h0)
        if len(self.hidden_layers) == 1:
            x = self.relu(x)
        for i, layer in enumerate(self.hidden_layers):
            if i > 0:
                x = self.keke_drop(x)
            x = layer(x)
            if i < len(self.hidden_layers) - 1:
                x = self.relu(x)

        return x

class RNN_LSTM(nn.Module):

    def __init__(self, hidden_sizes=[128], num_layers=2, num_classes=2, input_sz=128, batch_first=False, dropout=0.4):
        super(RNN_LSTM, self).__init__()
        self.hidden_sizes = hidden_sizes
        self.hidden_layers = nn.ModuleList()
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.input_lstm = input_sz
        self.batch_first = batch_first
        self.dropout = dropout

        self.lstm = nn.LSTM(input_sz, self.hidden_sizes[0], self.num_layers, batch_first=self.batch_first, dropout=self.dropout)
        self.relu = nn.ReLU()
        self.keke_drop = nn.Dropout(p=0.5)

        for k in range(len(self.hidden_sizes)):
            if k < len(self.hidden_sizes)-1:
                self.hidden_layers.append(nn.Linear(self.hidden_sizes[k], self.hidden_sizes[k+1]))
            else:
                self.hidden_layers.append(nn.Linear(self.hidden_sizes[k], self.num_classes))

    def forward(self, x):
        if torch.cuda.is_available():
            h0 = torch.zeros(self.num_layers, x.size(1), self.hidden_sizes[0]).cuda()
            c0 = torch.zeros(self.num_layers, x.size(1), self.hidden_sizes[0]).cuda()
        else:
            h0 = torch.zeros(self.num_layers, x.size(1), self.hidden_sizes[0])
            c0 = torch.zeros(self.num_layers, x.size(1), self.hidden_sizes[0])

        x, _ = self.lstm(x, (h0, c0))
        if len(self.hidden_layers) == 1:
            x = self.relu(x)
        for i, layer in enumerate(self.hidden_layers):
            if i > 0:
                x = self.keke_drop(x)
            x = layer(x)
            if i < len(self.hidden_layers) - 1:
                x = self.relu(x)        # fully-connected layer

        return x

class Exp:

    def __init__(self, name, model, train_loader, test_loader, learningrate=0.001, num_epochs=10, collector=None):
        self.name = name
        self.model = model
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.learningrate = learningrate
        self.num_epochs = num_epochs
        self.collector = collector

    def train(self):
        self.model.train()
        if torch.cuda.is_available():
            self.model.cuda()
        else:
            self.model.cpu()

        loss = nn.CrossEntropyLoss()
        optimizer = torch.optim.RMSprop(self.model.parameters(), lr=self.learningrate)

        for epoch in range(self.num_epochs):
            for idx, (data, target) in enumerate(self.train_loader.data_loader):
                if torch.cuda.is_available():
                    data, target = data.cuda(), target.cuda()
                data = data.view(data.size(0), -1, 41)
                optimizer.zero_grad()
                output = self.model(data)
                output = output.view(-1, 2)
                loss_value = loss(output, target)
                loss_value.backward()
                optimizer.step()

    def test(self):
        self.model.eval()

        total = 0
        correct = 0
        yo = []
        test_len = len(self.test_loader.data_loader.dataset)
        if torch.cuda.is_available():
            self.model.cuda()
        else:
            self.model.cpu()
        with torch.no_grad():
            for idx, (data, target) in enumerate(self.test_loader.data_loader):
                if torch.cuda.is_available():
                    data, target = data.cuda(), target.cuda()
                data = data.view(data.size(0), -1, 41)
                output = self.model(data)
                output = output.view(-1, 2)
                output = F.softmax(output, dim=1)
                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += ( predicted == target).sum()
                predicted_np = predicted.numpy()
                yo.append(predicted_np)

        yo = np.array([yo]).reshape(test_len, -1)
        yo_test = self.test_loader.ys.numpy()
        acc = accuracy_score(yo_test, yo)
        fScore = f1_score(yo_test, yo)

        if self.collector is not None:
           self.collector.collect(self.name, (acc, fScore))

        return (acc, fScore)
