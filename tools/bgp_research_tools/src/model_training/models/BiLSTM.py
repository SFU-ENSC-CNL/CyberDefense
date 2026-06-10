import keras
"""
## Build a model
Based On:
https://www.omdena.com/blog/time-series-classification-model-tutorial

"""
def bilstm_make_model(input_shape, num_classes):
    input_layer = keras.layers.Input(shape=input_shape, name="TIMESERIES_INPUT")
    # RNN Layers
    # layer - 1
    rec_layer_one = keras.layers.Bidirectional(
                        keras.layers.LSTM(128,
                            kernel_regularizer=keras.regularizers.l2(0.01),
                            recurrent_regularizer=keras.regularizers.l2(0.01),
                            return_sequences=True)
                        ,name ="BIDIRECTIONAL_LAYER_1")(input_layer)
    rec_layer_one = keras.layers.Dropout(0.1,name ="DROPOUT_LAYER_1")(rec_layer_one)
    
    # layer - 2
    rec_layer_two = keras.layers.Bidirectional(
                        keras.layers.LSTM(64,
                            kernel_regularizer=keras.regularizers.l2(0.01),
                            recurrent_regularizer=keras.regularizers.l2(0.01))
                        ,name ="BIDIRECTIONAL_LAYER_2")(rec_layer_one)
    rec_layer_two = keras.layers.Dropout(0.1,name ="DROPOUT_LAYER_2")(rec_layer_two)
    
    combined_dense_two = keras.layers.Dense(64, activation='relu',name="DENSE_LAYER_2")(rec_layer_two)
    # output_layer = keras.layers.Dense(num_classes, activation="softmax")(combined_dense_two)
    output_layer = keras.layers.Dense(num_classes, activation="sigmoid")(combined_dense_two)

    return keras.models.Model(inputs=input_layer, outputs=output_layer)


bilstm_callbacks = [
    # keras.callbacks.ModelCheckpoint(
    #     "best_model.keras", save_best_only=True, monitor="val_loss"
    # ),
    keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=20, min_lr=0.0001, verbose=0
    ),
    # keras.callbacks.EarlyStopping(monitor="val_loss", patience=50, verbose=0),
]