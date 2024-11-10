import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle

def insert_user_data(data):
    model = pickle.load(open("EASIEST/model.sav", "rb"))

    # Create a DataFrame with the user data
    user_df = pd.DataFrame(data)
    
    # Predict using the trained model
    predictions = model.predict(user_df)
    
    # Display overall predictions with percentages
    overall_prediction = "ASD" if predictions.mean() < 0.5 else "Non-ASD"


    print(f"\nOverall Prediction: {overall_prediction}")
    return overall_prediction

#The warning and the resulting nan values for the T-statistic and p-value are likely due to the fact that the variable correct is exactly equal to 0.5 in some iterations. This causes the denominator in the calculation (correct / 100) - 0.5 to be zero, leading to a division by zero issue and subsequent warnings.
# Menu
# while True:
#     print("\nMenu:")
#     print("1. Insert user data manually")
#     print("2. Exit")
#
#     choice = input("Enter your choice: ")
#
#     if choice == '1':
#         insert_user_data(model_glm)
#     elif choice == '2':
#         break
#     else:
#         print("Invalid choice. Please enter a valid option.")
