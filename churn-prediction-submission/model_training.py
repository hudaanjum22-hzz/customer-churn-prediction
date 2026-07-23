import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

# Import shared preprocessor
from preprocessing import ChurnPreprocessor

def train_and_evaluate(csv_path="data/customer_churn_data.csv", models_dir="models"):
    """
    Cleans data, runs train/test split with stratification, fits preprocessor,
    trains and evaluates multiple models, selects the best one, and serializes it.
    """
    os.makedirs(models_dir, exist_ok=True)
    
    print("\n" + "="*50)
    print("MODEL TRAINING AND EVALUATION")
    print("="*50)
    
    # 1. Load dataset
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Run data generation first.")
        
    df = pd.read_csv(csv_path)
    
    # 2. Extract features and label
    # Handle missing labels if any (drop rows where Churn is NaN)
    df = df.dropna(subset=["Churn"])
    
    # Detect and remove duplicate records (FR6)
    dupes = df.duplicated().sum()
    if dupes > 0:
        print(f"Detected {dupes} duplicate records. Removing them from the dataset...")
        df = df.drop_duplicates()
        
    X = df.drop(columns=["Churn"])
    y = df["Churn"].map({"Yes": 1, "No": 0})
    
    # 3. Stratified Train/Test Split (80/20) (FR20)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Train set shape: {X_train_raw.shape}, positive rate: {y_train.mean():.2%}")
    print(f"Test set shape: {X_test_raw.shape}, positive rate: {y_test.mean():.2%}")
    
    # 4. Preprocessing Fit & Transform (FR23, FR25)
    # Fit preprocessor strictly on training data to prevent leakage
    preprocessor = ChurnPreprocessor()
    X_train = preprocessor.fit_transform(X_train_raw)
    
    # Transform test data using fitted preprocessor
    X_test = preprocessor.transform(X_test_raw)
    
    # 5. Define Candidate Models (FR21)
    models = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=6),
        "Random Forest": RandomForestClassifier(random_state=42, n_estimators=150, max_depth=8)
    }
    
    results = {}
    best_f1 = -1.0
    best_model_name = None
    best_model_obj = None
    
    # 6. Train and Evaluate each model (FR22)
    for name, clf in models.items():
        print(f"\n--- Training {name} ---")
        clf.fit(X_train, y_train)
        
        # Predict
        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)[:, 1] if hasattr(clf, "predict_proba") else [None] * len(y_pred)
        
        # Calculate Metrics
        acc = accuracy_score(y_test, y_pred)
        
        # Precision, recall, f1 for class 'Yes' (represented as 1)
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary', pos_label=1)
        
        results[name] = {
            "Accuracy": acc,
            "Precision (Yes)": prec,
            "Recall (Yes)": rec,
            "F1-score (Yes)": f1,
            "Model": clf
        }
        
        print(f"Accuracy: {acc:.4f}")
        print(f"Precision (Yes): {prec:.4f}")
        print(f"Recall (Yes): {rec:.4f}")
        print(f"F1-score (Yes): {f1:.4f}")
        
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Track best model based on F1-score of the Churn (Yes) class
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model_obj = clf
            
    # 7. Print Comparison Report
    print("\n" + "="*40)
    print("MODEL COMPARISON SUMMARY")
    print("="*40)
    comparison_df = pd.DataFrame(results).T.drop(columns=["Model"])
    print(comparison_df.to_string())
    print("="*40)
    
    print(f"\nSelected Best Model: {best_model_name} (F1-score on Churn class: {best_f1:.4f})")
    
    # Check if we met target criteria: Accuracy >= 80% and F1 >= 0.75
    best_accuracy = results[best_model_name]["Accuracy"]
    met_accuracy = best_accuracy >= 0.80
    met_f1 = best_f1 >= 0.75
    
    print(f"Success Criteria Check:")
    print(f"  Target Accuracy >= 80.0%: {'PASSED' if met_accuracy else 'FAILED'} ({best_accuracy:.2%})")
    print(f"  Target F1-score >= 0.75: {'PASSED' if met_f1 else 'FAILED'} ({best_f1:.4f})")
    
    # 8. Save Champion Model and Preprocessor (FR23)
    model_path = os.path.join(models_dir, "churn_model.pkl")
    prep_path = os.path.join(models_dir, "preprocessor.pkl")
    
    joblib.dump(best_model_obj, model_path)
    joblib.dump(preprocessor, prep_path)
    
    print(f"\nSaved best model to: {model_path}")
    print(f"Saved fitted preprocessor to: {prep_path}")
    print("="*50 + "\n")
    
    return comparison_df

if __name__ == "__main__":
    train_and_evaluate()
