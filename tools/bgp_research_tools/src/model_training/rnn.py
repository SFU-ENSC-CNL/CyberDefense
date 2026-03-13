
import torch
import torch.nn as nn
from torch.autograd import Variable

class RNN(nn.Module):
    
    def __init__(self, hidden_size, num_layers, input_lstm, num_classes):
        super(RNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # Define the LSTM module
        self.lstm = nn.LSTM(input_lstm, hidden_size, num_layers, batch_first=False, dropout=0.4)

        # Define ReLU layer
        self.relu = nn.ReLU()

        # Define the Dropout layer with 0.5 dropout rate
        self.keke_drop = nn.Dropout(p=0.5)

        # Define a fully-connected layer fc4 with 32 inputs and 2 outputs
        self.fc4 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):

        if torch.cuda.is_available():
            h0 = Variable(torch.zeros(self.num_layers, x.size(1), self.hidden_size).cuda())
            c0 = Variable(torch.zeros(self.num_layers, x.size(1), self.hidden_size).cuda())
        else:
            h0 = Variable(torch.zeros(self.num_layers, x.size(1), self.hidden_size))
            c0 = Variable(torch.zeros(self.num_layers, x.size(1), self.hidden_size))

        x, _ = self.lstm(x, (h0, c0))  # LSTM network, c is the state

        x = self.relu(x)               # ReLU()

        x = self.fc4(x)                # fully-connected layer
        return x