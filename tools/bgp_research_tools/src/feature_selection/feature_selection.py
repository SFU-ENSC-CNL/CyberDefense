from sklearn.ensemble import ExtraTreesClassifier
import os
import pandas as pd
import numpy as np
from dataset.dataset import Dataset

class ExtraTreesFeatureSelection:

    def __init__(self, training_dataset):

        if (not isinstance(training_dataset, Dataset)):
            raise Exception(f"The argument dataset must be a instance of Dataset class. Instead {type(training_dataset)} were provided.")
        
        if not len(training_dataset.df) > 0:
            raise Exception(f"The trainning dataset must to have at least one data point")

        # Removing undesired columns
        df = training_dataset.df.drop(['HOUR', 'MINUTE', 'SECOND', 'TRAIN', 'DATETIME', 'POSIXTIME'], axis=1, errors='ignore')
        self.dataset = Dataset(df)

    def getImportancesDataFrame(self, n_estimators=100, random_state=1):
        np.random.seed(1)
        model = ExtraTreesClassifier(n_estimators=n_estimators, random_state=random_state)

        x, y = self.dataset.get_x_y()

        model.fit(x, y)

        feature_importance = model.feature_importances_

        # Normalizing the individual importances
        # feature_importance_normalized = np.std([tree.feature_importances_ for tree in
        #                                 model.estimators_],
        #                                 axis = 0)
        
        # Creating a DataFrame with the the Feature Selection result
        df = pd.DataFrame(feature_importance, index=self.dataset.get_features_columns(), columns=['importance'])
        df.sort_values(by=['importance'], ascending=False, inplace=True)
        return df
    
    # Extremely Randomized Trees Classifier(Extra Trees Classifier)    
    # Important to pass just the TRAINING DATASET
    def getSelectedFeatures(self, topFeatures=10, n_estimators=100, random_state=1):
        df = self.getImportancesDataFrame(n_estimators=n_estimators, random_state=random_state)
        return list(df.iloc[:topFeatures].index)
        

