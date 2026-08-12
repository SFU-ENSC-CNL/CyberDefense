import numpy as np
import torch
from torch import nn
import torch.utils.data as Data
import torch.nn.functional as F
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score


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
    def __init__(self, hidden_size=128, num_layers=2, num_classes=2, input_lstm=128,batch_first=False,dropout=0.4):
        super(RNN_GRU, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.input_lstm = input_lstm
        self.batch_first = batch_first
        self.dropout = dropout

        self.gru = nn.GRU(input_lstm, self.hidden_size, self.num_layers, batch_first=self.batch_first, dropout=self.dropout)

        # Define ReLU layer
        self.relu = nn.ReLU()

        # Define the Dropout layer with 0.5 dropout rate
        self.keke_drop = nn.Dropout(p=0.5)

        # Define a fully-connected layer fc4 with 32 inputs and 2 outputs
        self.fc4 = nn.Linear(self.hidden_size, self.num_classes)

    def forward(self, x):
        if torch.cuda.is_available():
            h0 = torch.zeros(self.num_layers, x.size(1), self.hidden_size).cuda()
        else:
            h0 = torch.zeros(self.num_layers, x.size(1), self.hidden_size)

        x, _ = self.gru(x, h0)  # GRU network

        x = self.relu(x)         # ReLU()

        x = self.fc4(x)          # fully-connected layer
        return x

class RNN_LSTM(nn.Module):
    def __init__(self, hidden_size=128, num_layers=2, num_classes=2, input_lstm=128,batch_first=False,dropout=0.4):
        super(RNN_LSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_classes = num_classes
        self.input_lstm = input_lstm
        self.batch_first = batch_first
        self.dropout = dropout

        self.lstm = nn.LSTM(input_lstm, self.hidden_size, self.num_layers, batch_first=self.batch_first, dropout=self.dropout)

        # Define ReLU layer
        self.relu = nn.ReLU()

        # Define the Dropout layer with 0.5 dropout rate
        self.keke_drop = nn.Dropout(p=0.5)

        # Define a fully-connected layer fc4 with 32 inputs and 2 outputs
        self.fc4 = nn.Linear(self.hidden_size, self.num_classes)

    def forward(self, x):
        if torch.cuda.is_available():
            h0 = torch.zeros(self.num_layers, x.size(1), self.hidden_size).cuda()
            c0 = torch.zeros(self.num_layers, x.size(1), self.hidden_size).cuda()
        else:
            h0 = torch.zeros(self.num_layers, x.size(1), self.hidden_size)
            c0 = torch.zeros(self.num_layers, x.size(1), self.hidden_size)

        x, _ = self.lstm(x, (h0,c0))  # GRU network

        x = self.relu(x)         # ReLU()

        x = self.fc4(x)          # fully-connected layer
        return x

class Exp:

    def __init__(self, name, model, train_loader, test_loader, learningrate=0.001, num_epochs=10):
        self.name = name
        self.model = model
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.learningrate = learningrate
        self.num_epochs = num_epochs

    def train(self):
        self.model.train()
        if torch.cuda.is_available():
            self.model.cuda()
        else:
            self.model.cpu()

        loss = nn.CrossEntropyLoss()
        optimizer = torch.optim.RMSprop(self.model.parameters(), lr=self.learningrate)
        #optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learningrate)

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
        for idx, (data, target) in enumerate(self.test_loader.data_loader):
            if torch.cuda.is_available():
                data, target = data.cuda(), target.cuda()
            data = data.view(self.test_loader.batch_size, -1, 41)
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

        print("Accuracy: %.4f, Fsocre %.4f" % (acc*100, fScore*100))



