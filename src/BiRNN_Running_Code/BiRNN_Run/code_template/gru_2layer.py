# -*- coding: utf-8 -*-
"""
@author Zhida Li <zhidal@sfu.ca>
@date Nov. 28, 2018

@copyright Copyright (c) Nov. 28, 2018                    ZHIDA LI
    All Rights Reserved

"""
######################################################
##### GRU2 (2 hidden layers) using BGP datasets #####
######################################################
# Import the Python libraries
import time

import numpy as np

import torch

import torch.nn as nn



import torch.nn.functional as F



import torch.utils.data as Data

from scipy.stats import zscore
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
import math
def replaceNan(matrix):
    for row in range(0, matrix.shape[0]):
        for col in range(0, matrix.shape[1]):

            if math.isnan(matrix[row, col]):
                matrix[row, col] = 0.0

    return

def ConfusionMatrix(y_true, y_pred):
    TP = 0
    FN = 0
    FP = 0
    TN = 0
    # Find the labels for anomaly and regular classes
    y_anomalyRef = 1
    y_regularRef = 0
    # for y_true_i in y_true:
    #     if y_true_i != 1:
    #         y_regularRef = y_true_i
    #     break
    # Calculate TP FN FP TN
    for i in range(len(y_true)): 
        if y_true[i]==y_pred[i]==y_anomalyRef:
            TP += 1
        elif (y_true[i]!=y_pred[i]) and (y_pred[i]==y_regularRef):
            FN += 1
        elif (y_true[i]!=y_pred[i]) and (y_pred[i]==y_anomalyRef):
            FP += 1
        elif y_true[i]==y_pred[i]==y_regularRef:
            TN += 1
        else:
            print("Please check input vectors.")
            print(y_regularRef)

    return (TP, FN, FP, TN)

import csv
import os


# os.environ["CUDA_VISIBLE_DEVICES"]=""



# Set the seed for generating random numbers on all GPUs.
torch.manual_seed(1) 
torch.cuda.manual_seed_all(1)




### Hyper parameters ####
parent_dirname = os.path.basename(os.path.dirname(os.path.realpath(__file__)));
num_feature = 41    # number of the features for input matrix

if parent_dirname.find("5") != -1:
    batch_size = 5;
elif parent_dirname.find("10") != -1:
    batch_size = 10;
else:
    batch_size = 20;




sequence_length = batch_size     # length of the input time sequence
input_size = num_feature
input_lstm = num_feature

hidden_size = HIDDEN_SIZE_3_HERE  # hidden size for fc4
num_layers = NUM_OF_LAYER_HERE    # number of layers for LSTM algorithm
num_classes = 2   # number of the class






num_epochs = NUM_EPOCHS_HERE   # number of the epochs
learning_rate = 0.001    # learning rate for optimization






train_filename = next((f for f in os.listdir(parent_dirname) if f.endswith('train.csv')));
test_filename = next((f for f in os.listdir(parent_dirname) if f.endswith('test.csv')));



train_filename = str(os.path.abspath(parent_dirname)) + "/" + str(train_filename)
test_filename = str(os.path.abspath(parent_dirname)) + "/" + str(test_filename)


print(train_filename)
print(test_filename)



### Load the datasets, x: data, y: label ####
trainDataset = np.loadtxt(train_filename, delimiter=",")    # change the datasets here
train_data_x = trainDataset[:, 0:-1]
train_label_y= trainDataset[:, -1]

testDataset = np.loadtxt(test_filename, delimiter=",")      # change the datasets here
test_data_x = testDataset[:, 0:-1]
test_label_y = testDataset[:, -1]


train_data_x = zscore(train_data_x, axis=0, ddof=1)
replaceNan(train_data_x)

test_data_x = zscore(test_data_x, axis=0, ddof=1)
replaceNan(test_data_x)

# Convert numpy to torch tensor
train_data_x, train_label_y = torch.from_numpy(train_data_x), torch.from_numpy(train_label_y)
test_data_x, test_label_y = torch.from_numpy(test_data_x), torch.from_numpy(test_label_y)



# Tensor
# floatTensor for training data, and longTensor for the label
    # FloatTensor = 32-bit floating
train_data,test_data = train_data_x.type(torch.FloatTensor), test_data_x.type(torch.FloatTensor) 
    # LongTensor = 64-bit integer
train_label,test_label = train_label_y.type(torch.LongTensor),test_label_y.type(torch.LongTensor)

print('train_data size:', train_data.size(),'train_label size:', train_label.size(),'\n',\
    'test_data size:', test_data.size(),'test_label size:', test_label.size())


test_len = test_label.size()[0];




# Data Loader (Input Pipeline)
# torch_dataset_train = Data.TensorDataset(data_tensor=train_data,
#                                         target_tensor=train_label)

# torch_dataset_test = Data.TensorDataset(data_tensor=test_data,
#                                         target_tensor=test_label)

torch_dataset_train = Data.TensorDataset(train_data,train_label)
torch_dataset_test = Data.TensorDataset(test_data,test_label)





#print torch_dataset_train,torch_dataset_test
train_loader = Data.DataLoader(dataset=torch_dataset_train,  # torch TensorDataset format
                               batch_size=batch_size,
                               shuffle=False)

test_loader = Data.DataLoader(dataset=torch_dataset_test,
                              batch_size=batch_size,
                              shuffle=False)


#### Build the deep learning models with 2 hidden layers (one layer: GRU, one layer: fc4) ###

class RNN(nn.Module):
    def __init__(self):
        super(RNN, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # Define the GRU module
        self.gru = nn.GRU(input_lstm, hidden_size, num_layers, batch_first=False, dropout=0.4, bidirectional=True)

        # Define ReLU layer
        self.relu = nn.ReLU()

        # Define the Dropout layer with 0.5 dropout rate
        self.keke_drop = nn.Dropout(p=0.5)

        # Define a fully-connected layer fc4 with 32 inputs and 2 outputs
        self.fc4 = nn.Linear(hidden_size*2, num_classes)

    def forward(self, x):
        # Set initial states: h_0 (num_layers * num_directions, batch, hidden_size)
        # x=input (seq_len, batch, input_size)
        
        if torch.cuda.is_available():
            h0 = torch.zeros(self.num_layers*2, x.size(1), self.hidden_size).cuda()
        else:
            h0 = torch.zeros(self.num_layers*2, x.size(1), self.hidden_size)

        x, _ = self.gru(x, h0)  # GRU network

        x = self.relu(x)         # ReLU()

        x = self.fc4(x)          # fully-connected layer
        return x



rnn = RNN()
start = time.perf_counter()
rnn.train()

if torch.cuda.is_available():
    rnn.cuda()
else:
    rnn.cpu()






# Select criterion for loss
criterion = nn.CrossEntropyLoss()

# Select an optimizer
optimizer = torch.optim.Adam(rnn.parameters(), lr=learning_rate)           # or Adam





print("batch size : " , batch_size);
print("test_len : " , test_len);
print("hidden_size1 : " , hidden_size);







### Train the model ###
for epoch in range(num_epochs):
    for i, (train, labels) in enumerate(train_loader):                        # load the data
        #x = Variable(train.view(sequence_length, -1, input_lstm)).cuda()      # reshape x to (time_step, batch, input_size)
        # y = Variable(labels).cuda()                                           # batch labels
        if torch.cuda.is_available():
            x = train.view(sequence_length, -1, input_lstm).cuda()
            y = labels.cuda()
        else:
            x = train.view(sequence_length, -1, input_lstm)
            y = labels


        # Forward + Backward + Optimize
        outputs = rnn(x)                                                      # RNN output
        outputs = outputs.view(-1, 2)

        loss = criterion(outputs, y)                                          # cross entropy loss
        optimizer.zero_grad()                                                 # clear gradients for this training step
        loss.backward()                                                       # back-propagation, compute gradients
        optimizer.step()                                                      # apply gradients


end = time.perf_counter()







### Test the model using evaluation mode ###
correct = 0
total = 0

rnn.eval()          # evaluation mode for testing
yo = []
for test, l in test_loader:
    if torch.cuda.is_available():
        p = test.view(sequence_length, -1, input_lstm).cuda()
    else:
        p = test.view(sequence_length, -1, input_lstm)


    outputs2 = rnn(p)
    outputs2 = outputs2.view(-1, 2)
    outputs2 = F.softmax(outputs2, dim=1)     # softmax function
    # print 'output2 size:', outputs2.size()

    _, predicted = torch.max(outputs2.data, 1)
    total += l.size(0)  # l.size(0)=100
    if torch.cuda.is_available():
        predicted = predicted.cpu()
    correct += (predicted == l).sum()
    predicted_np = predicted.numpy()
    yo.append(predicted_np)                # predicted labels, yo shape is (1, 72, 100, 1)

yo = np.array([yo]).reshape(test_len, -1)  
yo_test = test_label_y.numpy()
acc = accuracy_score(yo_test, yo)
fScore = f1_score(yo_test, yo)

recall = recall_score(yo_test, yo)
precision = precision_score(yo_test, yo)
TP, FN, FP, TN = ConfusionMatrix(yo_test, yo)
print(TP, FN, FP, TN)






# Save the accuracy and F-Score
with open(parent_dirname + "_accuracy.txt", "w") as text_file:
    text_file.write("Accuracy: %.4f, Fsocre %.4f" % (acc*100, fScore*100))


# Save the running time
with open(parent_dirname + "_runtime.txt", "w") as text_file:
    text_file.write("Run Time: %.4f" % (end-start))


model_pkl = 'rnn-gru2-%d' % sequence_length
torch.save(rnn.state_dict(), '%s.pkl'%model_pkl)


# Save the recall and precision
with open(parent_dirname + "_recallprecision.txt", "w") as text_file:
    text_file.write("Precision: %.4f, Recall %.4f, \n \
        TP %d, FP %d, TN %d, FN %d" % (precision*100, recall*100, TP, FP, TN, FN))

model_pkl = 'birnn-gru2-%d' % sequence_length
torch.save(rnn.state_dict(), '%s.pkl'%model_pkl)
