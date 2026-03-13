# import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, f1_score, precision_score, recall_score
import pandas as pd
import numpy as np
import os
from model_evaluation.plots import plot_model_train_val_loss
import json
from pathlib import Path

# This function can be called to evaluate the model against the train and test partitions
# def univariate_autoencoder_evaluation_report(model, X, Y):

#     X_tensor = torch.tensor(X, dtype=torch.float32)
#     # Evaluate the autoencoder on test data
#     model.eval()
#     with torch.no_grad():
#         reconstructed_data = model(X_tensor)
#         reconstruction_loss = torch.mean((X_tensor - reconstructed_data)**2, dim=1).numpy()

#     # Define a threshold for anomaly detection (e.g., based on the reconstruction error distribution)
#     threshold = np.mean(reconstruction_loss) + 2 * np.std(reconstruction_loss)

#     # Detect anomalies
#     anomalies = X[reconstruction_loss > threshold]

#     # Reconstruct X axis with X_ground_truth, X_predicted and anomaly flag
#     df = pd.DataFrame(data = X, columns=['ground_truth_signal'])
    
#     # Just try to plot the reconstructed signal just when this signal has 2 dimensions
#     # On the cases that LSTM is used and the reconstructed signal is as sequence
#     # we have many reconstructed signals for the same data point in a way that the
#     # sliding window is crossing
#     if len(reconstructed_data) == 2:
#         df['reconstructed_signal'] = reconstructed_data
#     df['threshold'] = threshold
#     df['reconstruction_loss'] = reconstruction_loss
#     df['predicted_label'] = np.where(df['reconstruction_loss'] > threshold,1,0)
#     df['prediction_score'] = np.where(df['predicted_label'] == Y,1,0)
    
#     return df, threshold

def save_evaluation_details(location, model, history, x_test, y_test, save=False):

    if save:
        # Creating folder if not exists
        Path(location).mkdir(parents=True, exist_ok=True)

    #Train and Test Loss
    test_loss, test_acc = model.evaluate(x_test, y_test)
    print("Test accuracy", test_acc)
    print("Test loss", test_loss)
    plot_train_val_los_filepath = os.path.join(location, "train_val_loss.png")
    if save:
        plot_model_train_val_loss(history, file_path=plot_train_val_los_filepath)

    # Getting predictions
    # For each data point returns a tuple with the
    # probabilities to be class 0 (regular) or class 1 (anomalous)
    Y_pred_prob = model.predict(x_test, verbose=0)

    # Select the class with the max probability
    # Arg max return the index of the element with the max value
    # The axis=-1 parameter says to do this evaluation in the last dimension
    y_pred  = np.argmax(Y_pred_prob, axis=-1)

    # Checking shapes
    if (len(y_pred) != len(y_test)):
        raise Exception(f"Number of predictions different from number from y_test. Check the code.")
    # if (len(y_pred) != len(dataset_test)):
    #     raise Exception(f"Number of predictions different from dataset_test. Check the code.")
    eval_metrics = calculate_metrics(y_test, y_pred, will_print=False)

    if save:
        metrics_filepath = os.path.join(location, "eval_metrics.json")
        with open(metrics_filepath, "w") as metrics_file:
            json.dump(eval_metrics, metrics_file, indent=4, default=str)

    return eval_metrics, y_pred


def calculate_metrics(y_test, y_pred, will_print=True):

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    precision = precision_score(y_test, y_pred, zero_division=np.nan)
    recall = recall_score(y_test, y_pred, zero_division=np.nan)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=np.nan)
    report_txt = classification_report(y_test, y_pred, output_dict=False, zero_division=np.nan)

    if (will_print):
    #Calculating metrics
        print("#"*60)
        print(f"Accuracy: {acc}")
        print(f"F1 score: {f1}")
        print(f"Correct predictions: ")
        print(f" TP: {tp}")
        print(f" TN: {tn}")
        print(f"Incorrect predictions: ")
        print(f" FP: {fp}")
        print(f" FN: {fn}")
        print()
        print(report_txt)
        print("#"*60)

    return dict({
        "accuracy": acc,
        "f1_score": f1,
        "cf_matrix_tp": float(tp),
        "cf_matrix_tn": float(tn),
        "cf_matrix_fp": float(fp),
        "cf_matrix_fn": float(fn),
        "precision": precision,
        "recall": precision,
        "classification_report": report,
    })
