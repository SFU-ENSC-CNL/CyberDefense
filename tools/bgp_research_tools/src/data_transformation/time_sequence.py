import pandas as pd
import numpy as np

# Definitions:
# X is the Pandas DataFrame containing the features values over the time
# y is the Pandas DataFrame containing the label values (class target) over the time
# T is the duration (amount of data points) of each time sequence that will be created
# F is the number of features present on X
# N is the number of data points present in X, len(X)
# len(y) is the number of data points in y inputs, that is expected to be in the same size of N
#
# Input:
#   X, y, T
#
# Output:
#   X_time_sequences, shape (N, T, F)
#   y_shifted, shape (N, 1)
#
# Output explanation:
#   This method return just (len(X) - time_steps) time sequences
#   Each element returned is a time sequence with T sequential values of X and a only one respective label for this time sequence
#   The label returned is aligned with the last data point of the respective time sequence
# Giving more details:
#   The time sequences returned are a sliding window
#   First element returned:
#       On X_time_sequences the first time sequence returned corresponds to the values of X from 0 to (0 + T), having the shape (T, F)
#       On y_shifted is returned the label element 0 + T on y, having shape (1,)
#       This means that the first T-1 labels are skipped
#   Second element returned:
#       On X_time_sequences the first time sequence returned corresponds to the values of X from 1 to (1 + T), having the shape (T, F)
#       On y_shifted is returned the label element 1 + T on y, having shape (1,)
#   Last element returned:
#       On X_time_sequences the first time sequence returned corresponds to the values of X from len(X)-T to len(X), having the shape (T, F)
#       On y_shifted is returned the label element len(X) on y, having shape (1,)
# 
def create_sequence_dataset(X, y, time_steps=1, prepend_x=False, prepend_y=False):
    Xs, ys = [], []

    if not (isinstance(X, pd.DataFrame) and (isinstance(y, pd.DataFrame) or isinstance(y, pd.Series))):
        print(type(X), type(y))
        raise Exception(f"X and y need to be Pandas DataFrame")

    if not (len(X) == len(y)):
        raise Exception(f"X and y need to have the same size in the first dimension, this means the same number of data points.")

    # Prepending feature
    # If both prepend_x and prepend_y are passed
    # The X and y will be prepend with the passed data
    # This is useful to add on beginning of testing the last T-1 data points
    if (prepend_x is not False and prepend_y is not False) \
        and (len(prepend_x) == len(prepend_y)
        and len(prepend_x) >= time_steps):
        X = pd.concat([prepend_x.tail(time_steps-1), X], ignore_index=True)
        y = pd.concat([prepend_y.tail(time_steps-1), y], ignore_index=True)
    # In Python, intervals are not inclusive, this means that is required to to add 1,
    # in order to the last element accessed will be (len(X) - time_steps) element
    for i in range(len(X) - time_steps + 1):
        # Intervals are not inclusive
        v = X.iloc[i:(i + time_steps)].values
        Xs.append(v)
        # But direct addressing is exact (inclusive)
        ys.append(y.iloc[i + time_steps - 1])
       
    return np.array(Xs), np.array(ys)