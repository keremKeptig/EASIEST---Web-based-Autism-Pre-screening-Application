import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import ExtraTreesClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import copy
import pickle


def insert_user_data2(data_to_send):
        model = pickle.load(open("EASIEST/model_2.sav", "rb"))
        # Predict class for participant
        predictions = model.predict(data_to_send)
        classification = sum(predictions) / len(predictions)  # Assuming predictions are binary (ASD: 1, TD: 0)

        # Print participant ID and predicted class with accuracy
        print(f"Participant ID: {1}, Predicted Class: {'ASD' if classification > 0.5 else 'TD'}")

        overall_prediction = "ASD" if classification > 0.5 else "Non-ASD"

        print(f"\nOverall Prediction: {overall_prediction}")
        return overall_prediction
