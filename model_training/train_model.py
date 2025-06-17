import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# --- 1. Define Paths ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "creditcard.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "fraud_detection_model.joblib")

def train_fraud_model():
    """
    Loads credit card transaction data, trains a logistic regression model
    to detect fraud, and saves the trained model to a file.
    """
    print("🚀 Starting model training process...")

    # --- 2. Load Data ---
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)

    # --- 3. Prepare Data for Training ---
    print("Preparing data...")
    # 'Class' is our target variable: 0 for a normal transaction, 1 for fraud.
    # All other columns are our features.
    X = df.drop('Class', axis=1)
    y = df['Class']

    # Split data into a training set (to teach the model) and a testing set (to evaluate it).
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Data split into training set ({len(X_train)} rows) and testing set ({len(X_test)} rows).")

    # --- 4. Train the Machine Learning Model ---
    print("Training the Logistic Regression model...")
    # We use class_weight='balanced' to help the model learn effectively,
    # since there are far more normal transactions than fraudulent ones.
    model = LogisticRegression(class_weight='balanced', max_iter=1000, solver='liblinear')
    model.fit(X_train, y_train)
    print("Model training complete.")

    # --- 5. Evaluate Model Performance ---
    print("\nEvaluating model performance on the unseen test set:")
    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions))

    # --- 6. Save the Trained Model ---
    # First, ensure the 'models' directory exists.
    os.makedirs(MODELS_DIR, exist_ok=True)
    print(f"Saving trained model to {MODEL_PATH}...")
    # Use the joblib library to save the model object to a single file.
    joblib.dump(model, MODEL_PATH)

    print("✅ Model training and saving process complete.")

if __name__ == "__main__":
    train_fraud_model()