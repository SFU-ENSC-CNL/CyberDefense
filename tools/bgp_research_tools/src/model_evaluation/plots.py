import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import matplotlib


"""
## Visualize curve samples

Here we visualize one timeseries example for each class in the dataset.

"""
def plot_samples(x_train, y_train, y_test, columns):

    classes = np.unique(np.concatenate((y_train, y_test), axis=0))

    
    plt.figure()

    for n in range(1,4):

        for c_idx, column in enumerate(columns):
            plt.clf()
            for c in classes:
                c_x_train = x_train[y_train == c]
                # Getting the N occurrence on the desired class
                sample = c_x_train[0]
                # Getting just the desired column from the time sequence 
                sample = [s[c_idx] for s in sample]
                plt.plot(sample, label=f"{column} class " + str(c))
            
            plt.legend(loc="best")
            plt.title(f"Sample nº {n}/3 for column {column}")
            plt.show()
        
        
    plt.close()

def plot_model_train_val_loss(history, file_path=False):
    """
    ## Plot the model's training and validation loss
    """

    metric = "sparse_categorical_accuracy"
    plt.figure()
    plt.plot(history.history[metric])
    plt.plot(history.history["val_" + metric])
    plt.title("model " + metric)
    plt.ylabel(metric, fontsize="large")
    plt.xlabel("epoch", fontsize="large")
    plt.legend(["train", "val"], loc="best")
    if (file_path):
        plt.savefig(file_path)
    else:
        plt.show()
    plt.close()


def plot_overview_chart(dataset_train, dataset_test, y_pred, columns, title, html_path=False):

    # Creating a local and independent copy
    dataset_train = dataset_train.df.copy(deep=True)
    dataset_test = dataset_test.df.copy(deep=True)

    # Adjusting y_pred value just for plot
    y_pred = list(map(lambda x: float(str(x).replace("1", "1.8")),y_pred))

    dataset_test.loc[:,'y_pred'] = y_pred
    dataset_train.loc[:,'is_train'] = -10
    dataset_test.loc[:,'is_test'] = -10

    graph_df = pd.concat([dataset_train,dataset_test], ignore_index=True)

    graph_df['LABEL'] = list(map(lambda x: float(str(x).replace("1", "2")),graph_df['LABEL']))

    traces = []

    dates = graph_df['datetime'] if 'datetime' in graph_df.columns else (graph_df['DATETIME'] if 'DATETIME' in graph_df.columns else graph_df.index)

    # Creating traces for the signals
    for column in columns:
        traces.append(
            go.Scatter(
            x = dates,
            y = graph_df[column],
            mode = 'lines',
            line={'width': 0.75},
            name = column,
            visible='legendonly'
            ))
        print(f"column:  {column}, shape: {dataset_test[column].shape}")

    traces.append(
            go.Scatter(
            x = dates,
            y = graph_df['LABEL'],
            mode = 'lines',
            fill='tozeroy',
            fillcolor='rgba(255,0,0,0.15)',
            line={'width': 0},
            name = 'Label'
    ))
    traces.append(go.Scatter(
        x = dates,
        y = graph_df['y_pred'],
        mode = 'lines',
        fill='tozeroy',
        fillcolor='rgba(0,0,255,0.15)',
        line={'width': 0},
        name = 'Predicted label',
    ))
    traces.append(go.Scatter(
        x = dates,
        y = graph_df['is_train'],
        mode = 'lines',
        fill='tozeroy',
        fillcolor='rgba(0,255,0,0.15)',
        # fillpattern=dict({"shape":"."}),
        line={'width': 0},
        name = 'Training partition',
    ))
    traces.append(go.Scatter(
        x = dates,
        y = graph_df['is_test'],
        mode = 'lines',
        fill='tozeroy',
        fillcolor='rgba(255,0,255,0.15)',
        # fillpattern=dict({"shape":"."}),
        line={'width': 0},
        name = 'Test partition',
    ))
    layout = go.Layout(
        title = title,
        xaxis = {'title' : "Date"},
        yaxis = {'title' : "Values"}
    )
    fig = go.Figure(data=traces, layout=layout)
    if (html_path):
        fig.write_html(html_path)
    else:
        fig.show()