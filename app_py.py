# -*- coding: utf-8 -*-
"""app.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1P5yY3CKu4sDJQyFPgMMuW6bSAPbnozr6
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, accuracy_score, mean_absolute_error, mean_squared_error, r2_score
import gradio as gr

# Function to load data
def load_data(file):
    data = pd.read_excel(file.name)
    return data

# Function to add anomaly detection columns based on the provided rules
def add_anomaly_columns(data):
    data['Anomaly'] = (
        ((data['a1'] == 0) & ((data['a2'] > 0) | (data['a3'] > 0))) |
        ((data['a2'] == 0) & ((data['a1'] > 0) | (data['a3'] > 0))) |
        ((data['a3'] == 0) & ((data['a1'] > 0) | (data['a2'] > 0)))
    )
    return data

# Function to add feature engineering columns
def add_features(data):
    data['mean_a'] = data[['a1', 'a2', 'a3']].mean(axis=1)
    data['std_a'] = data[['a1', 'a2', 'a3']].std(axis=1)
    return data

# Function to prepare data for classification
def prepare_classification_data(data):
    features = ['a1', 'a2', 'a3', 'mean_a', 'std_a']
    X = data[features]
    y = data['Anomaly']
    return X, y

# Function to calculate regression metrics and return the model
def calculate_regression_metrics(data, a_col):
    valid_mask = (data[a_col] != 0)
    X = data[valid_mask][[a_col]].values
    y = data[valid_mask][a_col].values

    model = RandomForestRegressor(random_state=42)
    model.fit(X, y)
    y_pred = model.predict(X)

    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)

    return mae, rmse, r2, model

def process_data(file):
    data = load_data(file)
    data = add_anomaly_columns(data)
    data = add_features(data)
    X, y = prepare_classification_data(data)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Random Forest Classifier
    rf_model = RandomForestClassifier(random_state=42)
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)

    # Calculate accuracy and classification report
    accuracy_rf = accuracy_score(y_test, y_pred_rf)
    report_rf = classification_report(y_test, y_pred_rf, output_dict=True)

    # Save the anomalies to a new Excel file with sorting
    anomalies = data[data['Anomaly'] == True]
    anomalies_sorted = anomalies.sort_values(by='mean_a', ascending=False)
    anomalies_file_path = 'anomalies_sorted.xlsx'
    anomalies_sorted.to_excel(anomalies_file_path, index=False)

    # Generate a plot
    fig, ax = plt.subplots()
    for a_col in ['a1', 'a2', 'a3']:
        mae, rmse, r2, model = calculate_regression_metrics(data, a_col)
        valid_mask = (data[a_col] != 0)
        X = data[valid_mask][[a_col]].values
        y = data[valid_mask][a_col].values
        y_pred = model.predict(X)

        ax.scatter(X, y, label=f'Actual Data ({a_col})')
        sorted_idx = X.flatten().argsort()
        ax.plot(X[sorted_idx], y_pred[sorted_idx], label=f'Regression Line ({a_col})')

    ax.set_xlabel('Amperes')
    ax.set_ylabel('Values')
    ax.set_title('Regression Analysis')
    ax.legend()
    plt.tight_layout()
    plt.savefig('/content/plot.png')

    return accuracy_rf, report_rf, anomalies_file_path, '/content/plot.png'

# Define the Gradio interface
interface = gr.Interface(
    fn=process_data,
    inputs=gr.File(label="Upload your Excel file"),
    outputs=[
        gr.Textbox(label="Accuracy"),
        gr.JSON(label="Classification Report"),
        gr.File(label="Download Anomalies"),
        gr.Image(label="Regression Plot")
    ],
    live=True
)

# Launch the Gradio app
interface.launch()