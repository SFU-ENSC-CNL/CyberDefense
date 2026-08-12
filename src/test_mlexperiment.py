#import unittest
import mlexperiment
import unittest
import os
import numpy as np
import torch

class TestMLExperiment(unittest.TestCase):

    def test_mlexperiment_gru_5(self):
        torch.manual_seed(1)
        train_loader = mlexperiment.Loader("../test_data/train.csv",batch_size=5)
        test_loader = mlexperiment.Loader("../test_data/test.csv",batch_size=5)
        model = mlexperiment.RNN_GRU(hidden_size=32, num_layers=1, num_classes=2, input_lstm=41, batch_first=False, dropout=0.4)
        experiment = mlexperiment.Exp("test",model,train_loader,test_loader,num_epochs=30)
        experiment.train()
        print("GRU-5")
        experiment.test()
        assert(True)

    def test_mlexperiment_gru_10(self):
        torch.manual_seed(1)
        train_loader = mlexperiment.Loader("../test_data/train.csv",batch_size=10)
        test_loader = mlexperiment.Loader("../test_data/test.csv",batch_size=10)
        model = mlexperiment.RNN_GRU(hidden_size=32, num_layers=1, num_classes=2, input_lstm=41, batch_first=False, dropout=0.4)
        experiment = mlexperiment.Exp("test",model,train_loader,test_loader,num_epochs=30)
        experiment.train()
        print("GRU-10")
        experiment.test()
        assert(True)

    def test_mlexperiment_gru_20(self):
        torch.manual_seed(1)
        train_loader = mlexperiment.Loader("../test_data/train.csv",batch_size=20)
        test_loader = mlexperiment.Loader("../test_data/test.csv",batch_size=20)
        model = mlexperiment.RNN_GRU(hidden_size=32, num_layers=1, num_classes=2, input_lstm=41, batch_first=False, dropout=0.4)
        experiment = mlexperiment.Exp("test",model,train_loader,test_loader,num_epochs=30)
        experiment.train()
        print("GRU-20")
        experiment.test()
        assert(True)

    def test_mlexperiment_lstm_5(self):
        torch.manual_seed(1)
        train_loader = mlexperiment.Loader("../test_data/train.csv",batch_size=5)
        test_loader = mlexperiment.Loader("../test_data/test.csv",batch_size=5)
        model = mlexperiment.RNN_LSTM(hidden_size=32, num_layers=1, num_classes=2, input_lstm=41, batch_first=False, dropout=0.4)
        experiment = mlexperiment.Exp("test",model,train_loader,test_loader,num_epochs=30)
        experiment.train()
        print("LSTM-5")
        experiment.test()
        assert(True)

    def test_mlexperiment_lstm_10(self):
        torch.manual_seed(1)
        train_loader = mlexperiment.Loader("../test_data/train.csv", batch_size=10)
        test_loader = mlexperiment.Loader("../test_data/test.csv", batch_size=10)
        model = mlexperiment.RNN_LSTM(hidden_size=32, num_layers=1, num_classes=2, input_lstm=41, batch_first=False, dropout=0.4)
        experiment = mlexperiment.Exp("test", model, train_loader, test_loader, num_epochs=30)
        experiment.train()
        print("LSTM-10")
        experiment.test()
        assert (True)

    def test_mlexperiment_lstm_20(self):
        torch.manual_seed(1)
        train_loader = mlexperiment.Loader("../test_data/train.csv", batch_size=20)
        test_loader = mlexperiment.Loader("../test_data/test.csv", batch_size=20)
        model = mlexperiment.RNN_LSTM(hidden_size=32, num_layers=1, num_classes=2, input_lstm=41, batch_first=False, dropout=0.4)
        experiment = mlexperiment.Exp("test", model, train_loader, test_loader, num_epochs=30)
        experiment.train()
        print("LSTM-20")
        experiment.test()
        assert (True)