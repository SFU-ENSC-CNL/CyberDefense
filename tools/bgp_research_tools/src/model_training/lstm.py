import sys
from model_training.rnn import RNN

# Set the seed for generating random numbers on all GPUs.
torch.manual_seed(1) 
torch.cuda.manual_seed_all(1)

# DATASET PARAMETERS
# data partition strategy and proportion 
# 
#
# HYPER PARAMETERS
# batch_size: 
# num_layers: 
# hidden_size
# number of classes
# number of epochs
# learning_rate

class LSTM:

    def __init__(train_dataset,
                test_dataset,
                num_layers,
                hidden_size,
                dropout):

        self.sequence_length = batch_size
        # self.input_size = train_dataset.get_number_features()
        # self.input_lstm = train_dataset.get_number_features()

        torch_dataset_train = Data.TensorDataset(train_data,
                                         train_label)

        torch_dataset_test = Data.TensorDataset(test_data,
                                        test_label)

        self.train_loader = Data.DataLoader(dataset=torch_dataset_train,  # torch TensorDataset format
                                    batch_size=batch_size,
                                    shuffle=False)

        self.test_loader = Data.DataLoader(dataset=torch_dataset_test,
                                    batch_size=batch_size,
                                    shuffle=False)

        self.rnn = RNN()
        

    def train():
        start = time.clock()
        self.rnn.train()

        if torch.cuda.is_available():
            self.rnn.cuda()
        else:
            self.rnn.cpu()

        # Select criterion for loss
        criterion = nn.CrossEntropyLoss()

        # Select an optimizer
        optimizer = torch.optim.RMSprop(self.rnn.parameters(), lr=learning_rate)           # or Adam
        ### Train the model ###
        for epoch in range(num_epochs):
            for i, (train, labels) in enumerate(self.train_loader):                        # load the data
                if torch.cuda.is_available():
                    x = Variable(train.view(sequence_length, -1, input_lstm)).cuda()  # reshape x to (time_step, batch, input_size)
                    y = Variable(labels).cuda()                                       # batch labels
                else:
                    x = Variable(train.view(sequence_length, -1, input_lstm))
                    y = Variable(labels)
                # Forward + Backward + Optimize
                outputs = self.rnn(x)                                                      # RNN output
                outputs = outputs.view(-1, 2)
                loss = criterion(outputs, y)                                          # cross entropy loss
                optimizer.zero_grad()                                                 # clear gradients for this training step
                loss.backward()                                                       # back-propagation: compute gradients
                optimizer.step()                                                      # apply gradients
                #if (i + 1) % 20 == 0:
                #   print ('Epoch [%d/%d], Step [%d/%d], Loss: %.4f'
                #        % (epoch + 1, num_epochs, i + 1, len(trainDataset) // batch_size, loss.item()))

        end = time.clock()

    def eval():
        ### Test the model using evaluation mode ###
        correct = 0
        total = 0

        rnn.eval()  # evaluation mode for testing
        yo = []
        for test, l in test_loader:
            if torch.cuda.is_available():
                p = Variable(test.view(sequence_length, -1, input_lstm)).cuda()
            else:
                p = Variable(test.view(sequence_length, -1, input_lstm))
            outputs2 = rnn(p)
            outputs2 = outputs2.view(-1, 2)
            outputs2 = F.softmax(outputs2)

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

