import mlexperiment
import unittest
import torch
import json
import math

class TestMLExperiment(unittest.TestCase):

    tol = 0.005


    def test_GRU(self):
        batches = [5,10,20]
        layers = [ [32], [32,16], [80,32,16]]
        collector = mlexperiment.StatsCollector()
        for layer in layers:
            for batch in batches:
                name = "gru_layers:" + str(layer) + "_batch:" + str(batch)
                torch.manual_seed(1)
                train_loader = mlexperiment.Loader("../test_data/train.csv",batch_size=batch)
                test_loader = mlexperiment.Loader("../test_data/test.csv",batch_size=batch)
                model = mlexperiment.RNN_GRU(hidden_sizes=layer, num_layers=1, num_classes=2, input_sz=41, batch_first=False, dropout=0.0)
                experiment = mlexperiment.Exp(name,model,train_loader,test_loader,num_epochs=30,collector=collector)
                experiment.train()
                experiment.test()

        with open('../test_data/gru_gold.json') as f:
            gold = json.load(f)
            for key in gold:
                self.assertTrue(key in collector.data)
                (u, v) = collector.data[key]
                (up, vp) = gold[key]
                self.assertTrue(math.isclose(v,vp, rel_tol=TestMLExperiment.tol))
                self.assertTrue(math.isclose(u,up, rel_tol=TestMLExperiment.tol))


    def test_LSTM(self):
        batches = [5,10,20]
        layers = [ [32], [32,16], [80,32,16]]
        collector = mlexperiment.StatsCollector()
        for layer in layers:
            for batch in batches:
                name = "lstm_layers:" + str(layer) + "_batch:" + str(batch)
                torch.manual_seed(1)
                train_loader = mlexperiment.Loader("../test_data/train.csv",batch_size=batch)
                test_loader = mlexperiment.Loader("../test_data/test.csv",batch_size=batch)
                model = mlexperiment.RNN_LSTM(hidden_sizes=layer, num_layers=1, num_classes=2, input_sz=41, batch_first=False, dropout=0.0)
                experiment = mlexperiment.Exp(name,model,train_loader,test_loader,num_epochs=30, collector=collector)
                experiment.train()
                experiment.test()

        with open('../test_data/lstm_gold.json') as f:
            gold = json.load(f)
            for key in gold:
                self.assertTrue(key in collector.data)
                (u, v) = collector.data[key]
                (up, vp) = gold[key]
                self.assertTrue(math.isclose(v,vp, rel_tol=TestMLExperiment.tol))
                self.assertTrue(math.isclose(u,up, rel_tol=TestMLExperiment.tol))

    def test_Bi_GRU(self):
        batches = [5,10,20]
        layers = [ [32], [32,16], [80,32,16]]
        collector = mlexperiment.StatsCollector()
        for layer in layers:
            for batch in batches:
                name = "gru_layers:" + str(layer) + "_batch:" + str(batch)
                torch.manual_seed(1)
                train_loader = mlexperiment.Loader("../test_data/train.csv",batch_size=batch)
                test_loader = mlexperiment.Loader("../test_data/test.csv",batch_size=batch)
                model = mlexperiment.RNN_GRU(hidden_sizes=layer, num_layers=1, num_classes=2, input_sz=41, batch_first=False, dropout=0.0, bidrectional=True)
                experiment = mlexperiment.Exp(name,model,train_loader,test_loader,num_epochs=30,collector=collector)
                experiment.train()
                experiment.test()

        with open('../test_data/bi_gru_gold.json') as f:
            gold = json.load(f)
            for key in gold:
                self.assertTrue(key in collector.data)
                (u, v) = collector.data[key]
                (up, vp) = gold[key]
                self.assertTrue(math.isclose(v,vp, rel_tol=TestMLExperiment.tol))
                self.assertTrue(math.isclose(u,up, rel_tol=TestMLExperiment.tol))

    def test_Bi_LSTM(self):
        batches = [5,10,20]
        layers = [ [32], [32,16], [80,32,16]]
        collector = mlexperiment.StatsCollector()
        for layer in layers:
            for batch in batches:
                name = "lstm_layers:" + str(layer) + "_batch:" + str(batch)
                torch.manual_seed(1)
                train_loader = mlexperiment.Loader("../test_data/train.csv",batch_size=batch)
                test_loader = mlexperiment.Loader("../test_data/test.csv",batch_size=batch)
                model = mlexperiment.RNN_LSTM(hidden_sizes=layer, num_layers=1, num_classes=2, input_sz=41, batch_first=False, dropout=0.0, bidrectional=True)
                experiment = mlexperiment.Exp(name,model,train_loader,test_loader,num_epochs=30, collector=collector)
                experiment.train()
                experiment.test()

        with open('../test_data/bi_lstm_gold.json') as f:
            gold = json.load(f)
            for key in gold:
                self.assertTrue(key in collector.data)
                (u, v) = collector.data[key]
                (up, vp) = gold[key]
                self.assertTrue(math.isclose(v,vp, rel_tol=TestMLExperiment.tol))
                self.assertTrue(math.isclose(u,up, rel_tol=TestMLExperiment.tol))