import os
import keras
from pathlib import Path
import uuid
import json

def save_model_details(location, model):
    # Creating folder if not exists
    Path(location).mkdir(parents=True, exist_ok=True)
    # Saving model
    json_filepath = os.path.join(location,"model.json")
    with open(json_filepath, "w") as json_file:
        json_obj = json.loads(model.to_json())
        json.dump(json_obj, json_file, indent=4)
    # Saving Weights
    weights_filepath = os.path.join(location,"model.weights.h5")
    model.save_weights(weights_filepath)
    # Saving Summary
    summary_filepath = os.path.join(location,"summary.txt")
    with open(summary_filepath, "w") as summary_file:
        # Pass the file handle in as a lambda function to make it callable
        model.summary(print_fn=lambda x, line_break="\n": summary_file.write(f"{x}{line_break}"))
    # Plotting Model
    plot_filepath = os.path.join(location,"model.png")
    keras.utils.plot_model(model,
                           to_file=plot_filepath,
                           show_shapes=True,
                           show_layer_activations=True,
                           show_trainable=True)

# Generate a unique ID based on dataset and model parameters    
def get_model_hash(model, params, dataset_filepath):
    model_config = str(dataset_filepath) + str(params) + str(model.get_config())
    return str(uuid.uuid5(uuid.NAMESPACE_URL, model_config))



        

